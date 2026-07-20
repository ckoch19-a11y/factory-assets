import React from "react";
import { Link } from "react-router-dom";

export default function PageNotFound() {
  return (
    <main className="min-h-screen grid place-items-center bg-background px-6">
      <div className="text-center">
        <h1 className="text-display-md">Page introuvable</h1>
        <p className="mt-4 text-muted-foreground">Cette page n'existe pas ou n'existe plus.</p>
        <Link to="/" className="mt-8 inline-block rounded-full bg-primary text-primary-foreground px-6 py-3">
          Retour à l'accueil
        </Link>
      </div>
    </main>
  );
}
