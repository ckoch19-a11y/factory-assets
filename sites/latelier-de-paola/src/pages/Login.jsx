import React, { useEffect } from "react";
import { base44 } from "@/api/base44Client";

// CHOIX EXÉCUTANT : les pages d'authentification existent déjà côté Base44
// (recette, étape Base & Auth : « ne jamais les recréer, juste les brancher ») —
// cette route redirige vers le login hébergé de l'app.
export default function Login() {
  useEffect(() => {
    base44.auth.redirectToLogin();
  }, []);

  return (
    <main className="min-h-screen grid place-items-center bg-background px-6">
      <p className="text-muted-foreground">Redirection vers la page de connexion…</p>
    </main>
  );
}
