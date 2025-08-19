/// <reference types="react-scripts" />

// Create React App Environment Variables
declare namespace NodeJS {
  interface ProcessEnv {
    readonly REACT_APP_API_BASE_URL: string
    readonly REACT_APP_PUBLIC_APP_NAME: string
    readonly REACT_APP_CALENDLY_URL: string
    readonly REACT_APP_ENV_NAME: string
    readonly REACT_APP_STRIPE_PUBLISHABLE_KEY: string
    readonly REACT_APP_SENTRY_DSN: string
    readonly REACT_APP_SENTRY_ENVIRONMENT: string
    readonly REACT_APP_ENABLE_ANALYTICS: string
    readonly REACT_APP_ENABLE_CHAT_SUPPORT: string
    readonly REACT_APP_VERCEL_GIT_COMMIT_SHA: string
  }
}
