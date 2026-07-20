import { useQuery } from "@tanstack/react-query";
import { base44 } from "@/api/base44Client";

/* Hooks de lecture des entités (recette ?pipeline=1, étape vitrine) — chaque
   section garde un fallback issu du brief : le site n'est jamais cassé.
   CHOIX EXÉCUTANT : une seule requête SectionContenu.list() partagée entre
   toutes les sections (au lieu d'un filter() par clé) — même API de hook que la
   recette, moins d'allers-retours réseau. */

export function useSections() {
  return useQuery({
    queryKey: ["sections"],
    queryFn: () => base44.entities.SectionContenu.list(),
    initialData: [],
    retry: 1,
  });
}

export function useSection(cle, fallback = {}) {
  const { data } = useSections();
  const section = Array.isArray(data) ? data.find((s) => s.cle === cle) : null;
  return section && section.visible !== false ? { ...fallback, ...section } : fallback;
}

export function usePrestations() {
  return useQuery({
    queryKey: ["prestations"],
    queryFn: () => base44.entities.Prestation.list("ordre"),
    initialData: [],
    retry: 1,
  });
}

export function useTemoignages() {
  return useQuery({
    queryKey: ["temoignages"],
    queryFn: () => base44.entities.Temoignage.filter({ visible: true }, "-created_date", 12),
    initialData: [],
    retry: 1,
  });
}

export function useSiteConfig() {
  return useQuery({
    queryKey: ["siteconfig"],
    queryFn: async () => (await base44.entities.SiteConfig.list())[0] ?? {},
    initialData: {},
    retry: 1,
  });
}
