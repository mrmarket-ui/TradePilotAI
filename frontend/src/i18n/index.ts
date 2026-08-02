import i18n from "i18next"
import LanguageDetector from "i18next-browser-languagedetector"
import { initReactI18next } from "react-i18next"

const resources = {
  en: {
    translation: {
      dashboard: "Dashboard",
      tradeJournal: "Trade Journal",
      analytics: "Analytics",
      traderDNA: "Trader DNA",
      aiCoach: "AI Coach",
      strategyLab: "Strategy Lab",
      setupScorer: "Setup Scorer",
      reports: "Reports",
      partners: "Brokers & Partners",
      billing: "Billing",
      settings: "Settings",
      admin: "Admin",
      signOut: "Sign out",
      welcomeBack: "Welcome back",
      currentPlan: "Current plan",
      language: "Language",
      currency: "Preferred currency",
      savePreferences: "Save preferences",
    },
  },

  af: {
    translation: {
      dashboard: "Kontroleskerm",
      tradeJournal: "Handelsjoernaal",
      analytics: "Ontleding",
      traderDNA: "Handelaar-DNA",
      aiCoach: "KI-afrigter",
      strategyLab: "Strategielaboratorium",
      setupScorer: "Opstelling-telling",
      reports: "Verslae",
      partners: "Makelaars en vennote",
      billing: "Fakturering",
      settings: "Instellings",
      admin: "Administrasie",
      signOut: "Teken uit",
      welcomeBack: "Welkom terug",
      currentPlan: "Huidige plan",
      language: "Taal",
      currency: "Voorkeurgeldeenheid",
      savePreferences: "Stoor voorkeure",
    },
  },

  fr: {
    translation: {
      dashboard: "Tableau de bord",
      tradeJournal: "Journal de trading",
      analytics: "Analyses",
      traderDNA: "ADN du trader",
      aiCoach: "Coach IA",
      strategyLab: "Laboratoire de stratégie",
      setupScorer: "Évaluation des configurations",
      reports: "Rapports",
      partners: "Courtiers et partenaires",
      billing: "Facturation",
      settings: "Paramètres",
      admin: "Administration",
      signOut: "Se déconnecter",
      welcomeBack: "Bon retour",
      currentPlan: "Forfait actuel",
      language: "Langue",
      currency: "Devise préférée",
      savePreferences: "Enregistrer les préférences",
    },
  },

  es: {
    translation: {
      dashboard: "Panel",
      tradeJournal: "Diario de trading",
      analytics: "Analíticas",
      traderDNA: "ADN del trader",
      aiCoach: "Coach IA",
      strategyLab: "Laboratorio de estrategias",
      setupScorer: "Evaluador de configuraciones",
      reports: "Informes",
      partners: "Brókers y socios",
      billing: "Facturación",
      settings: "Configuración",
      admin: "Administración",
      signOut: "Cerrar sesión",
      welcomeBack: "Bienvenido de nuevo",
      currentPlan: "Plan actual",
      language: "Idioma",
      currency: "Moneda preferida",
      savePreferences: "Guardar preferencias",
    },
  },
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "en",
    supportedLngs: [
      "en",
      "af",
      "fr",
      "es",
    ],
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: [
        "localStorage",
        "navigator",
      ],
      caches: [
        "localStorage",
      ],
    },
  })

export default i18n
