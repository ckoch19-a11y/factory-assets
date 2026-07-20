import React, { Suspense, lazy } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "@/components/ProtectedRoute";
import Home from "@/pages/Home";
import Login from "@/pages/Login";
import PageNotFound from "@/pages/PageNotFound";

// CHOIX EXÉCUTANT : back-office et pages légales en import() dynamique —
// budget JS initial ≤ 180 KB gz (ASSEMBLAGE §6), le vitrine ne paie pas l'admin.
const MentionsLegales = lazy(() => import("@/pages/MentionsLegales"));
const Confidentialite = lazy(() => import("@/pages/Confidentialite"));
const AdminLayout = lazy(() => import("@/pages/admin/AdminLayout"));
const AdminDashboard = lazy(() => import("@/pages/admin/AdminDashboard"));
const AdminParametres = lazy(() => import("@/pages/admin/AdminParametres"));
const AdminContenu = lazy(() => import("@/pages/admin/AdminContenu"));
const AdminPrestations = lazy(() => import("@/pages/admin/AdminPrestations"));
const AdminAvis = lazy(() => import("@/pages/admin/AdminAvis"));
const AdminDemandes = lazy(() => import("@/pages/admin/AdminDemandes"));

const Attente = (
  <div className="min-h-screen grid place-items-center bg-background text-muted-foreground">Chargement…</div>
);

export default function App() {
  return (
    <Suspense fallback={Attente}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/mentions-legales" element={<MentionsLegales />} />
        <Route path="/confidentialite" element={<Confidentialite />} />
        <Route path="/login" element={<Login />} />
        {/* Back-office : réservé au rôle admin (brief §5), derrière la garde d'authentification. */}
        <Route element={<ProtectedRoute adminOnly unauthenticatedElement={<Navigate to="/login" replace />} />}>
          <Route element={<AdminLayout />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/parametres" element={<AdminParametres />} />
            <Route path="/admin/contenu" element={<AdminContenu />} />
            <Route path="/admin/prestations" element={<AdminPrestations />} />
            <Route path="/admin/avis" element={<AdminAvis />} />
            <Route path="/admin/demandes" element={<AdminDemandes />} />
          </Route>
        </Route>
        <Route path="*" element={<PageNotFound />} />
      </Routes>
    </Suspense>
  );
}
