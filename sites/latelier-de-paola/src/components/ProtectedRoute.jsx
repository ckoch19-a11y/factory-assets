import React, { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import { base44 } from "@/api/base44Client";

// CHOIX EXÉCUTANT : recréé localement — dans une app Base44 ce composant existe
// déjà (recette, étape Base & Auth) ; API identique (unauthenticatedElement),
// plus la garde de rôle admin exigée par le brief (§5 : /admin réservé au rôle admin).
export default function ProtectedRoute({ unauthenticatedElement = null, adminOnly = false }) {
  const [etat, setEtat] = useState({ statut: "chargement", user: null });

  useEffect(() => {
    let actif = true;
    base44.auth
      .me()
      .then((user) => actif && setEtat({ statut: "ok", user }))
      .catch(() => actif && setEtat({ statut: "anonyme", user: null }));
    return () => {
      actif = false;
    };
  }, []);

  if (etat.statut === "chargement") {
    return (
      <div className="min-h-screen grid place-items-center bg-background text-muted-foreground">
        Chargement…
      </div>
    );
  }
  if (etat.statut === "anonyme") return unauthenticatedElement;
  if (adminOnly && etat.user?.role !== "admin") {
    return (
      <main className="min-h-screen grid place-items-center bg-background px-6">
        <div className="max-w-md text-center">
          <h1 className="text-display-md">Accès réservé</h1>
          <p className="mt-4 text-muted-foreground">
            Cet espace est réservé aux administrateurs du site.
          </p>
          <a href="/" className="mt-8 inline-block rounded-full bg-primary text-primary-foreground px-6 py-3">
            Retour au site
          </a>
        </div>
      </main>
    );
  }
  return <Outlet context={{ user: etat.user }} />;
}
