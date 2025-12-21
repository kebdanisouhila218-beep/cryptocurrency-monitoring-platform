# collector/collector.py - VERSION CORRIGÉE AVEC FILTRE
import sys
import time
import requests
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)

# ===== ✅ LISTE DES 50 CRYPTOS POPULAIRES À COLLECTER =====
CRYPTO_LIST = [
    # Top 13 (déjà présentes)
    "btc-bitcoin",
    "eth-ethereum",
    "bnb-binance-coin",
    "sol-solana",
    "xrp-ripple",
    "ada-cardano",
    "doge-dogecoin",
    "dot-polkadot",
    "matic-polygon",
    "ltc-litecoin",
    "avax-avalanche",
    "link-chainlink",
    "atom-cosmos",
    "uni-uniswap",
    "xlm-stellar",
    
    # 35 cryptos supplémentaires
    "trx-tron",
    "etc-ethereum-classic",
    "bch-bitcoin-cash",
    "near-near-protocol",
    "leo-unus-sed-leo",
    "icp-internet-computer",
    "apt-aptos",
    "arb-arbitrum",
    "op-optimism",
    "stx-stacks",
    "fil-filecoin",
    "ldo-lido-dao",
    "mnt-mantle",
    "imx-immutable-x",
    "inj-injective-protocol",
    "mkr-maker",
    "rune-thorchain",
    "grt-the-graph",
    "aave-aave",
    "snx-synthetix-network-token",
    "ftm-fantom",
    "algo-algorand",
    "vet-vechain",
    "egld-elrond",
    "axs-axie-infinity",
    "sand-the-sandbox",
    "mana-decentraland",
    "theta-theta-network",
    "xtz-tezos",
    "flow-flow",
    "eos-eos",
    "chz-chiliz",
    "kcs-kucoin-shares",
    "btt-bittorrent",
    "hbar-hedera-hashgraph",
    "zil-zilliqa",
    "ksm-kusama",
    "gala-gala",
    "crv-curve-dao-token",
    "qnt-quant",
    "1inch-1inch",
    "neo-neo",
    "comp-compound",
    "zrx-0x",
    "enj-enjin-coin",
    "bat-basic-attention-token",
    "lrc-loopring",
    "chr-chromia"
]

MONGO_URI = "mongodb://mongo:27017/"
DB_NAME = "crypto_db"
COLLECTION_NAME = "prices"

def fetch_and_store():
    try:
        logging.info("📡 Appel à CoinPaprika...")
        
        # ✅ CORRECTION: Utiliser le paramètre ids pour filtrer
        coin_ids = ",".join(CRYPTO_LIST)
        url = f"https://api.coinpaprika.com/v1/tickers?ids={coin_ids}"
        
        logging.info(f"📋 Cryptos demandées: {len(CRYPTO_LIST)}")
        logging.info(f"🔗 URL: {url[:100]}...")
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        coins = response.json()
        
        logging.info(f"📦 Total de cryptos reçues : {len(coins)}")
        
        # Vérifier qu'on a bien reçu nos cryptos
        if len(coins) == 0:
            logging.error("❌ ERREUR: Aucune crypto reçue!")
            logging.info("🔍 Vérification de l'API...")
            
            # Essai de récupérer juste Bitcoin pour tester
            test_url = "https://api.coinpaprika.com/v1/tickers/btc-bitcoin"
            test_response = requests.get(test_url, timeout=10)
            
            if test_response.status_code == 200:
                logging.info("✅ L'API fonctionne, mais le filtre ne marche pas")
                logging.info("📝 Utilisation de la méthode alternative...")
                
                # Méthode alternative: récupérer toutes les cryptos et filtrer
                all_url = "https://api.coinpaprika.com/v1/tickers"
                all_response = requests.get(all_url, timeout=15)
                all_coins = all_response.json()
                
                # Filtrer pour garder seulement nos cryptos
                coins = [c for c in all_coins if c['id'] in CRYPTO_LIST]
                logging.info(f"✅ {len(coins)} cryptos filtrées")
            else:
                logging.error("❌ L'API ne répond pas correctement")
                return False
        
        # Afficher les cryptos récupérées
        logging.info("\n" + "="*60)
        logging.info("📊 CRYPTOS RÉCUPÉRÉES:")
        for coin in coins:
            logging.info(f"  ✅ {coin.get('symbol', 'N/A'):6s} - {coin.get('name', 'N/A')}")
        logging.info("="*60 + "\n")

        # Connexion MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        inserted = 0
        updated = 0
        current_timestamp = time.time()
        
        for coin in coins:
            try:
                # Vérifier que les données sont complètes
                if "quotes" not in coin or "USD" not in coin.get("quotes", {}):
                    logging.warning(f"⚠️ Données incomplètes pour {coin.get('id', 'unknown')}")
                    continue
                
                doc = {
                    "coin_id": coin["id"],
                    "symbol": coin["symbol"],
                    "name": coin["name"],
                    "price_usd": coin["quotes"]["USD"]["price"],
                    "volume_24h": coin["quotes"]["USD"].get("volume_24h", 0),
                    "market_cap": coin["quotes"]["USD"].get("market_cap", 0),
                    "percent_change_24h": coin["quotes"]["USD"].get("percent_change_24h", 0),
                    "timestamp": current_timestamp
                }
                
                # ✅ UPSERT : Remplacer au lieu d'accumuler
                result = collection.update_one(
                    {"symbol": coin["symbol"]},  # Recherche par symbole
                    {"$set": doc},                # Mise à jour
                    upsert=True                   # Insère si n'existe pas
                )
                
                if result.upserted_id:
                    inserted += 1
                    logging.info(f"✅ {coin['symbol']:6s} = ${doc['price_usd']:>12.4f} (NOUVEAU)")
                else:
                    updated += 1
                    logging.info(f"✅ {coin['symbol']:6s} = ${doc['price_usd']:>12.4f} (MIS À JOUR)")
            except Exception as e:
                logging.error(f"❌ Erreur pour {coin.get('symbol', 'unknown')}: {e}")

        logging.info(f"\n💾 {inserted} nouvelles cryptos, {updated} mises à jour.")
        
        # Afficher un résumé
        total_docs = collection.count_documents({})
        logging.info(f"📊 Total de documents dans la DB: {total_docs}")
        
        # Afficher les cryptos les plus récentes
        latest = list(collection.find({}, {"symbol": 1, "name": 1, "price_usd": 1, "_id": 0})
                     .sort("timestamp", -1).limit(5))
        logging.info("\n📈 Dernières cryptos en DB:")
        for crypto in latest:
            logging.info(f"  {crypto['symbol']:6s} - {crypto['name']}: ${crypto['price_usd']:.4f}")
        
        return True

    except Exception as e:
        logging.error(f"❌ Échec : {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Mode test : si on lance avec "test" → un seul run
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        logging.info("🧪 MODE TEST : exécution unique")
        success = fetch_and_store()
        if success:
            print("\n🟢 TEST RÉUSSI : données collectées et stockées.")
        else:
            print("\n🔴 TEST ÉCHOUÉ : voir les logs ci-dessus.")
        sys.exit(0 if success else 1)

    # Mode normal : boucle infinie
    logging.info("🚀 Collector en mode continu (toutes les 60s)...")
    while True:
        fetch_and_store()
        time.sleep(60)