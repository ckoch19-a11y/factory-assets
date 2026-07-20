import React from "react";

/* Contrôles de formulaire du back-office — tokens Steep (inputs fond muted
   radius 16px), partagés par tous les écrans CRUD. */

const classeInput =
  "w-full bg-muted rounded-input px-3.5 py-2.5 text-foreground placeholder:text-subtle border border-transparent focus:outline-none focus:border-foreground/30 disabled:opacity-60";

export function Champ({ label, value, onChange, type = "text", readOnly = false, placeholder = "" }) {
  return (
    <label className="block">
      <span className="block text-xs uppercase tracking-widest text-subtle mb-1.5">{label}</span>
      <input
        type={type}
        value={value ?? ""}
        onChange={(e) => onChange?.(type === "number" ? Number(e.target.value) : e.target.value)}
        readOnly={readOnly}
        disabled={readOnly}
        placeholder={placeholder}
        className={classeInput}
      />
    </label>
  );
}

export function ChampZone({ label, value, onChange, rows = 4 }) {
  return (
    <label className="block">
      <span className="block text-xs uppercase tracking-widest text-subtle mb-1.5">{label}</span>
      <textarea value={value ?? ""} onChange={(e) => onChange?.(e.target.value)} rows={rows} className={classeInput} />
    </label>
  );
}

export function Interrupteur({ label, checked, onChange }) {
  return (
    <label className="inline-flex items-center gap-2 cursor-pointer select-none">
      <input type="checkbox" checked={checked !== false} onChange={(e) => onChange?.(e.target.checked)} className="sr-only peer" />
      <span
        aria-hidden="true"
        className="w-9 h-5 rounded-full bg-muted peer-checked:bg-primary relative transition-colors after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:w-4 after:h-4 after:rounded-full after:bg-background after:transition-transform peer-checked:after:translate-x-4 border border-border"
      />
      <span className="text-sm text-muted-foreground">{label}</span>
    </label>
  );
}

export function BoutonPilule({ children, onClick, type = "button", ghost = false, disabled = false }) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={
        ghost
          ? "rounded-full border border-border bg-background text-foreground px-5 py-2 text-sm hover:bg-muted disabled:opacity-60"
          : "rounded-full bg-primary text-primary-foreground px-5 py-2 text-sm font-body-strong disabled:opacity-60"
      }
    >
      {children}
    </button>
  );
}
