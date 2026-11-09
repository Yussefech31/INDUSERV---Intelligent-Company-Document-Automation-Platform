import React from 'react';
import { ShieldCheck, Globe2, Building2 } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  companyName?: string;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  companyName = 'INDUSERV Technologies',
}) => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between shrink-0">
      <div>
        <h1 className="text-lg font-bold text-slate-900 tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs font-medium text-slate-700">
          <Building2 className="w-3.5 h-3.5 text-slate-500" />
          <span>{companyName}</span>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-emerald-600 bg-emerald-50 px-2.5 py-1.5 rounded-full border border-emerald-200">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
          <span className="font-medium">Calcul Déterministe Vérifié</span>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-slate-600 bg-slate-100 px-2.5 py-1.5 rounded-full">
          <Globe2 className="w-3.5 h-3.5 text-slate-500" />
          <span className="font-semibold">FR</span>
        </div>
      </div>
    </header>
  );
};

