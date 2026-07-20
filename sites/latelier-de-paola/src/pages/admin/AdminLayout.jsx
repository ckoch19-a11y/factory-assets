import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import { base44 } from "@/api/base44Client";

/* Layout back-office (recette, étape backoffice) : sidebar + Outlet,
   même registre que le vitrine en plus sobre (tokens Steep). */

const ECRANS = [
  { to: "/admin", label: "Tableau de bord", end: true },
  { to: "/admin/parametres", label: "Paramètres" },
  { to: "/admin/contenu", label: "Contenus" },
  { to: "/admin/prestations", label: "Prestations & tarifs" },
  { to: "/admin/avis", label: "Avis" },
  { to: "/admin/demandes", label: "Demandes" },
];

export default function AdminLayout() {
  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-background-alt">
      <aside className="md:w-60 shrink-0 border-b md:border-b-0 md:border-r border-border bg-background p-4 flex flex-col gap-1">
        <p className="font-heading text-lg px-3 py-2">L'Atelier de Paola</p>
        <nav aria-label="Navigation du back-office" className="flex md:flex-col gap-1 flex-wrap">
          {ECRANS.map((e) => (
            <NavLink
              key={e.to}
              to={e.to}
              end={e.end}
              className={({ isActive }) =>
                "px-3 py-2 rounded-input text-sm " +
                (isActive ? "bg-muted text-foreground font-body-strong" : "text-muted-foreground hover:bg-muted")
              }
            >
              {e.label}
            </NavLink>
          ))}
        </nav>
        <div className="md:mt-auto flex md:flex-col gap-1 pt-2">
          <a href="/" className="px-3 py-2 rounded-input text-sm text-muted-foreground hover:bg-muted">
            Voir le site →
          </a>
          <button
            type="button"
            onClick={() => base44.auth.logout()}
            className="text-left px-3 py-2 rounded-input text-sm text-muted-foreground hover:bg-muted"
          >
            Se déconnecter
          </button>
        </div>
      </aside>
      <main className="flex-1 p-6 max-w-4xl">
        <Outlet />
      </main>
    </div>
  );
}
