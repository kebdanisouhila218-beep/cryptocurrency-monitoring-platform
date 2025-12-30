#!/usr/bin/env python3
"""
Script de sauvegarde automatique de la base de données MongoDB
Usage:
    python backup_db.py                    # Sauvegarde complète
    python backup_db.py --collections users alerts  # Collections spécifiques
    python backup_db.py --restore backup_20241230_120000  # Restaurer
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient
from bson import json_util, ObjectId

# Configuration
MONGO_HOST = os.getenv("MONGO_HOST", "127.0.0.1")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
DB_NAME = "crypto_db"

# Dossier de sauvegarde
BACKUP_DIR = Path(__file__).parent.parent / "backups"


def get_db():
    """Connexion à MongoDB"""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # Test connexion
    return client[DB_NAME]


def backup_collection(db, collection_name: str, backup_path: Path) -> int:
    """Sauvegarde une collection en JSON"""
    collection = db[collection_name]
    documents = list(collection.find({}))
    
    # Convertir ObjectId en string pour JSON
    for doc in documents:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        # Convertir les datetime
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
    
    file_path = backup_path / f"{collection_name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False, default=str)
    
    return len(documents)


def backup_database(collections: list = None) -> str:
    """
    Sauvegarde complète ou partielle de la base de données
    
    Args:
        collections: Liste des collections à sauvegarder (None = toutes)
    
    Returns:
        Chemin du dossier de sauvegarde
    """
    print("🔄 Démarrage de la sauvegarde...")
    
    # Créer le dossier de sauvegarde
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"backup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)
    
    try:
        db = get_db()
        print(f"✅ Connexion MongoDB réussie")
        
        # Lister les collections
        if collections:
            collection_names = collections
        else:
            collection_names = db.list_collection_names()
        
        print(f"📁 Collections à sauvegarder: {collection_names}")
        
        # Sauvegarder chaque collection
        stats = {}
        total_docs = 0
        
        for name in collection_names:
            if name in db.list_collection_names():
                count = backup_collection(db, name, backup_path)
                stats[name] = count
                total_docs += count
                print(f"  ✅ {name}: {count} documents")
            else:
                print(f"  ⚠️ {name}: Collection non trouvée")
        
        # Sauvegarder les métadonnées
        metadata = {
            "timestamp": timestamp,
            "date": datetime.now().isoformat(),
            "database": DB_NAME,
            "collections": stats,
            "total_documents": total_docs
        }
        
        with open(backup_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Sauvegarde terminée!")
        print(f"📁 Dossier: {backup_path}")
        print(f"📊 Total: {total_docs} documents dans {len(stats)} collections")
        
        return str(backup_path)
        
    except Exception as e:
        print(f"❌ Erreur de sauvegarde: {e}")
        raise


def restore_collection(db, collection_name: str, backup_path: Path, drop_existing: bool = False) -> int:
    """Restaure une collection depuis un fichier JSON"""
    file_path = backup_path / f"{collection_name}.json"
    
    if not file_path.exists():
        print(f"  ⚠️ {collection_name}: Fichier non trouvé")
        return 0
    
    with open(file_path, "r", encoding="utf-8") as f:
        documents = json.load(f)
    
    if not documents:
        print(f"  ⚠️ {collection_name}: Aucun document")
        return 0
    
    collection = db[collection_name]
    
    # Supprimer la collection existante si demandé
    if drop_existing:
        collection.drop()
    
    # Convertir les _id string en ObjectId si possible
    for doc in documents:
        if "_id" in doc:
            try:
                doc["_id"] = ObjectId(doc["_id"])
            except:
                del doc["_id"]  # Laisser MongoDB générer un nouvel ID
    
    # Insérer les documents
    if documents:
        collection.insert_many(documents)
    
    return len(documents)


def restore_database(backup_name: str, collections: list = None, drop_existing: bool = False) -> bool:
    """
    Restaure la base de données depuis une sauvegarde
    
    Args:
        backup_name: Nom du dossier de sauvegarde (ex: backup_20241230_120000)
        collections: Liste des collections à restaurer (None = toutes)
        drop_existing: Si True, supprime les collections existantes avant restauration
    
    Returns:
        True si succès
    """
    print(f"🔄 Restauration depuis {backup_name}...")
    
    backup_path = BACKUP_DIR / backup_name
    
    if not backup_path.exists():
        print(f"❌ Dossier de sauvegarde non trouvé: {backup_path}")
        return False
    
    # Lire les métadonnées
    metadata_file = backup_path / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        print(f"📅 Sauvegarde du: {metadata.get('date', 'N/A')}")
        print(f"📊 Collections: {list(metadata.get('collections', {}).keys())}")
    
    try:
        db = get_db()
        print(f"✅ Connexion MongoDB réussie")
        
        # Lister les fichiers JSON
        if collections:
            json_files = [f"{c}.json" for c in collections]
        else:
            json_files = [f.name for f in backup_path.glob("*.json") if f.name != "metadata.json"]
        
        # Restaurer chaque collection
        stats = {}
        total_docs = 0
        
        for json_file in json_files:
            collection_name = json_file.replace(".json", "")
            count = restore_collection(db, collection_name, backup_path, drop_existing)
            stats[collection_name] = count
            total_docs += count
            print(f"  ✅ {collection_name}: {count} documents restaurés")
        
        print(f"\n✅ Restauration terminée!")
        print(f"📊 Total: {total_docs} documents dans {len(stats)} collections")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de restauration: {e}")
        return False


def list_backups():
    """Liste toutes les sauvegardes disponibles"""
    if not BACKUP_DIR.exists():
        print("📁 Aucune sauvegarde trouvée")
        return []
    
    backups = []
    for folder in sorted(BACKUP_DIR.iterdir(), reverse=True):
        if folder.is_dir() and folder.name.startswith("backup_"):
            metadata_file = folder / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                backups.append({
                    "name": folder.name,
                    "date": metadata.get("date", "N/A"),
                    "collections": list(metadata.get("collections", {}).keys()),
                    "total_documents": metadata.get("total_documents", 0)
                })
    
    print(f"\n📁 Sauvegardes disponibles ({len(backups)}):\n")
    for b in backups:
        print(f"  📦 {b['name']}")
        print(f"     Date: {b['date']}")
        print(f"     Collections: {', '.join(b['collections'])}")
        print(f"     Documents: {b['total_documents']}")
        print()
    
    return backups


def cleanup_old_backups(keep_count: int = 5):
    """Supprime les anciennes sauvegardes, garde les N plus récentes"""
    if not BACKUP_DIR.exists():
        return
    
    backups = sorted(
        [f for f in BACKUP_DIR.iterdir() if f.is_dir() and f.name.startswith("backup_")],
        reverse=True
    )
    
    if len(backups) <= keep_count:
        print(f"✅ {len(backups)} sauvegardes, rien à supprimer (max: {keep_count})")
        return
    
    to_delete = backups[keep_count:]
    for folder in to_delete:
        import shutil
        shutil.rmtree(folder)
        print(f"🗑️ Supprimé: {folder.name}")
    
    print(f"✅ {len(to_delete)} anciennes sauvegardes supprimées")


def main():
    parser = argparse.ArgumentParser(description="Sauvegarde/Restauration MongoDB")
    
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    # Commande backup
    backup_parser = subparsers.add_parser("backup", help="Créer une sauvegarde")
    backup_parser.add_argument(
        "--collections", "-c",
        nargs="+",
        help="Collections spécifiques à sauvegarder"
    )
    
    # Commande restore
    restore_parser = subparsers.add_parser("restore", help="Restaurer une sauvegarde")
    restore_parser.add_argument(
        "backup_name",
        help="Nom du dossier de sauvegarde"
    )
    restore_parser.add_argument(
        "--collections", "-c",
        nargs="+",
        help="Collections spécifiques à restaurer"
    )
    restore_parser.add_argument(
        "--drop",
        action="store_true",
        help="Supprimer les collections existantes avant restauration"
    )
    
    # Commande list
    subparsers.add_parser("list", help="Lister les sauvegardes")
    
    # Commande cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Supprimer anciennes sauvegardes")
    cleanup_parser.add_argument(
        "--keep", "-k",
        type=int,
        default=5,
        help="Nombre de sauvegardes à garder (défaut: 5)"
    )
    
    args = parser.parse_args()
    
    if args.command == "backup":
        backup_database(args.collections)
    elif args.command == "restore":
        restore_database(args.backup_name, args.collections, args.drop)
    elif args.command == "list":
        list_backups()
    elif args.command == "cleanup":
        cleanup_old_backups(args.keep)
    else:
        # Par défaut: sauvegarde complète
        backup_database()


if __name__ == "__main__":
    main()
