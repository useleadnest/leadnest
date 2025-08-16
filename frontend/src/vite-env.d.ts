/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_PUBLIC_APP_NAME: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
