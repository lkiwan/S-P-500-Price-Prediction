# Guide de Mise à Jour des Prix S&P 500

## 🎯 Options de Mise à Jour

Vous avez **3 façons** de mettre à jour les prix du S&P 500:

---

## ✅ **Option 1: Mise à Jour Automatique (RECOMMANDÉ)**

Le dashboard vérifie automatiquement les nouveaux prix **à chaque démarrage**.

### Comment ça marche:
1. **Au démarrage du Docker**, l'application vérifie automatiquement Yahoo Finance
2. Si de nouvelles données sont disponibles, vous verrez un message dans les logs
3. Les prix affichés sont **toujours les plus récents disponibles**

### Avantages:
- ✅ Aucune action requise
- ✅ Se met à jour automatiquement à chaque démarrage
- ✅ Affiche toujours les prix du jour

### Comment utiliser:
```bash
docker-compose restart
```
C'est tout! Les prix seront mis à jour automatiquement.

---

## 📊 **Option 2: Vérifier les Prix en Temps Réel (API)**

Vous pouvez vérifier les prix actuels **sans redémarrer** via l'API.

### Endpoints disponibles:

**1. Vérifier le statut du marché:**
```
http://localhost:5000/api/market_status
```
Affiche:
- Prix actuel en temps réel
- Changement depuis la veille
- Statut du marché (ouvert/fermé)
- Dernière mise à jour

**2. Vérifier si de nouvelles données sont disponibles:**
```
http://localhost:5000/api/update_prices
```
Affiche:
- Dernier prix disponible
- Si de nouvelles données existent
- Message vous indiquant si une mise à jour est nécessaire

### Comment utiliser dans le navigateur:
```
http://localhost:5000/api/market_status
```

### Exemple de réponse:
```json
{
  "success": true,
  "current_price": 6737.49,
  "previous_close": 6850.92,
  "change": -113.43,
  "change_pct": -1.66,
  "is_market_open": false,
  "last_update": "2025-11-13 10:30:00"
}
```

---

## 🔄 **Option 3: Mise à Jour Manuelle Complète**

Pour mettre à jour le fichier de données **et** régénérer toutes les fonctionnalités.

### Méthode Rapide (Windows):
Double-cliquez sur:
```
auto_update_prices.bat
```

Ce script va:
1. ✅ Télécharger les derniers prix depuis Yahoo Finance
2. ✅ Mettre à jour le fichier price_data.csv
3. ✅ Redémarrer le conteneur Docker
4. ✅ Afficher les nouvelles données

### Méthode Manuelle (Ligne de commande):
```bash
# 1. Mettre à jour les prix
python update_latest_data.py

# 2. Redémarrer Docker
docker-compose restart
```

### Quand utiliser cette méthode:
- Vous voulez archiver les données historiques complètes
- Vous voulez régénérer les prédictions
- Vous faites du backtesting
- Vous voulez les données dans le fichier CSV

---

## 📅 **Fréquence de Mise à Jour Recommandée**

### Utilisation Standard:
- **Journalière**: Redémarrez Docker chaque matin
  ```bash
  docker-compose restart
  ```

### Utilisation Active (Trading):
- **Plusieurs fois par jour**: Utilisez l'API en temps réel
  ```
  http://localhost:5000/api/market_status
  ```

### Utilisation Analytique:
- **Hebdomadaire**: Mise à jour manuelle complète
  ```bash
  python update_latest_data.py
  docker-compose restart
  ```

---

## 🤖 **Configuration Automatique Avancée**

### Task Scheduler Windows (Mise à jour quotidienne automatique):

**1. Créer une tâche planifiée:**
- Ouvrez "Planificateur de tâches" (Task Scheduler)
- Créez une nouvelle tâche
- Nom: "S&P 500 Auto Update"
- Déclencheur: Tous les jours à 9h00
- Action: Exécuter `auto_update_prices.bat`

**2. Détails de la tâche:**
```
Programme: C:\Windows\System32\cmd.exe
Arguments: /c "cd /d C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA && auto_update_prices.bat"
```

**3. Résultat:**
- ✅ Les prix se mettent à jour automatiquement chaque jour à 9h
- ✅ Docker redémarre automatiquement
- ✅ Dashboard toujours à jour

---

## 📊 **Vérifier l'État Actuel**

### Dans le dashboard:
```
http://localhost:5000
```
Le prix affiché provient toujours de Yahoo Finance en temps réel.

### Dans les logs Docker:
```bash
docker-compose logs -f
```
Vous verrez:
```
[AUTO-UPDATE] Fetching latest S&P 500 prices...
[AUTO-UPDATE] Data is up to date (Last: 2025-11-13)
```

---

## 🎯 **Comparaison des Méthodes**

| Méthode | Automatique | Temps Réel | Mise à Jour Fichier | Fréquence |
|---------|-------------|------------|---------------------|-----------|
| **Auto (au démarrage)** | ✅ Oui | ✅ Oui | ❌ Non | À chaque redémarrage |
| **API temps réel** | ✅ Oui | ✅ Oui | ❌ Non | Toujours |
| **Manuelle (script)** | ❌ Non | ✅ Oui | ✅ Oui | Quand vous voulez |
| **Task Scheduler** | ✅ Oui | ✅ Oui | ✅ Oui | Quotidien (configurable) |

---

## 💡 **Recommandations par Type d'Utilisateur**

### 👤 **Trader Actif:**
```bash
# Méthode: API temps réel
# Ouvrez dans un nouvel onglet:
http://localhost:5000/api/market_status

# Rafraîchissez cette page toutes les 5-15 minutes
```

### 📊 **Analyste/Chercheur:**
```bash
# Méthode: Mise à jour manuelle hebdomadaire
python update_latest_data.py
docker-compose restart

# Pour archiver les données
```

### 🏢 **Utilisateur Passif:**
```bash
# Méthode: Auto au démarrage
docker-compose restart  # Chaque matin

# Ou configurez Task Scheduler
```

---

## ❓ **FAQ**

### Q: Les prix se mettent-ils à jour automatiquement?
**R:** Oui, l'application vérifie Yahoo Finance **à chaque démarrage** du Docker. Redémarrez simplement le conteneur pour obtenir les derniers prix.

### Q: Dois-je exécuter update_latest_data.py tous les jours?
**R:** **Non!** Seulement si vous voulez mettre à jour le fichier CSV historique. Le dashboard affiche automatiquement les prix du jour au démarrage.

### Q: Comment voir les prix en temps réel sans redémarrer?
**R:** Utilisez l'endpoint API: `http://localhost:5000/api/market_status`

### Q: Le dashboard affiche-t-il toujours les prix actuels?
**R:** Oui! À chaque démarrage, l'app vérifie Yahoo Finance. Pour des mises à jour plus fréquentes, redémarrez le conteneur ou utilisez l'API.

### Q: Puis-je automatiser complètement les mises à jour?
**R:** Oui! Configurez Task Scheduler Windows pour exécuter `auto_update_prices.bat` chaque jour à l'heure souhaitée.

---

## 🚀 **Quick Start**

**Pour la plupart des utilisateurs:**

```bash
# Chaque matin:
docker-compose restart

# Ou en un clic:
# Double-cliquez sur auto_update_prices.bat
```

**Pour les traders actifs:**

```
Ajoutez aux favoris: http://localhost:5000/api/market_status
Rafraîchissez cette page régulièrement
```

---

## 📞 **Support**

Pour plus d'informations:
- Voir `TROUBLESHOOTING.md` pour les problèmes
- Voir `README_UPDATED.md` pour la documentation complète
- Ouvrir une issue sur GitHub

---

**✅ Le système est maintenant configuré pour des mises à jour automatiques!**

**Prix actuels visibles à:** http://localhost:5000

**Dernière mise à jour:** 13 novembre 2025
