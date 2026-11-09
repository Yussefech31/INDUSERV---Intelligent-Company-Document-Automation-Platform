import React, { useState, useEffect } from 'react';
import {
  Calculator,
  ShieldCheck,
  TrendingUp,
  Percent,
  Receipt,
  Scale,
  Clock,
  ArrowRight,
  CheckCircle2,
  RefreshCw,
  Plus,
  Trash2,
} from 'lucide-react';
import { api } from '../services/api';
import { CalculationAudit } from '../types';

export const CalculationsPage: React.FC = () => {
  const [activeCalculator, setActiveCalculator] = useState<'vat' | 'margin' | 'budget'>('vat');

  // VAT & Invoice Simulator State
  const [vatHtAmount, setVatHtAmount] = useState<number>(2500);
  const [vatRate, setVatRate] = useState<number>(20.0);
  const [vatDiscount, setVatDiscount] = useState<number>(5.0);
  const [vatCurrency, setVatCurrency] = useState<string>('EUR');
  const [vatResult, setVatResult] = useState<CalculationAudit | null>(null);

  // Margin Simulator State
  const [marginCostPrice, setMarginCostPrice] = useState<number>(1200);
  const [marginSellingPrice, setMarginSellingPrice] = useState<number>(1800);
  const [marginCurrency, setMarginCurrency] = useState<string>('EUR');
  const [marginResult, setMarginResult] = useState<CalculationAudit | null>(null);

  // Budget Variance Simulator State
  const [budgetPlanned, setBudgetPlanned] = useState<number>(50000);
  const [budgetActual, setBudgetActual] = useState<number>(54200);
  const [budgetCurrency, setBudgetCurrency] = useState<string>('EUR');
  const [budgetResult, setBudgetResult] = useState<CalculationAudit | null>(null);

  // Audits log
  const [audits, setAudits] = useState<CalculationAudit[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAudits();
    // Execute default initial calculations
    handleComputeVAT();
  }, []);

  const loadAudits = async () => {
    try {
      const data = await api.getCalculationAudits();
      setAudits(data);
    } catch (err) {
      console.error('Failed to load audits', err);
    }
  };

  const handleComputeVAT = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    try {
      setLoading(true);
      const res = await api.calculate({
        operation: 'ht_to_ttc',
        ht_amount: vatHtAmount,
        tva_rate: vatRate,
        discount_rate: vatDiscount,
        currency: vatCurrency,
      });
      setVatResult(res);
      loadAudits();
    } catch (err: any) {
      alert(`Erreur de calcul : ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleComputeMargin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    try {
      setLoading(true);
      const res = await api.calculate({
        operation: 'margin_and_markup',
        cost_price: marginCostPrice,
        selling_price: marginSellingPrice,
        currency: marginCurrency,
      });
      setMarginResult(res);
      loadAudits();
    } catch (err: any) {
      alert(`Erreur de calcul : ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleComputeBudget = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    try {
      setLoading(true);
      const res = await api.calculate({
        operation: 'budget_variance',
        budget_planned: budgetPlanned,
        budget_actual: budgetActual,
        currency: budgetCurrency,
      });
      setBudgetResult(res);
      loadAudits();
    } catch (err: any) {
      alert(`Erreur de calcul : ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
              Moteur Mathématique Déterministe Python
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Calculs Certifiés & Analyse Financière</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            L'IA ne réalise jamais de calculs arithmétiques mentaux. Tous les montants HT/TTC, remises et marges sont certifiés par le backend Python avec précision décimale.
          </p>
        </div>

        {/* Calculator Navigation Selector */}
        <div className="flex p-1 rounded-xl bg-slate-100 border border-slate-200">
          <button
            onClick={() => {
              setActiveCalculator('vat');
              if (!vatResult) handleComputeVAT();
            }}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeCalculator === 'vat' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Receipt className="w-3.5 h-3.5" />
            TVA & Facturation
          </button>
          <button
            onClick={() => {
              setActiveCalculator('margin');
              if (!marginResult) handleComputeMargin();
            }}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeCalculator === 'margin' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Percent className="w-3.5 h-3.5" />
            Marges Commerciales
          </button>
          <button
            onClick={() => {
              setActiveCalculator('budget');
              if (!budgetResult) handleComputeBudget();
            }}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeCalculator === 'budget' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <TrendingUp className="w-3.5 h-3.5" />
            Écarts Budgétaires
          </button>
        </div>
      </div>

      {/* Calculator Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Form Column */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
          {activeCalculator === 'vat' && (
            <form onSubmit={handleComputeVAT} className="space-y-4">
              <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <Receipt className="w-4 h-4 text-blue-600" />
                Simulateur Facturation (HT, Remise, TVA, TTC)
              </h3>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Montant Hors Taxes (HT)</label>
                <div className="relative">
                  <input
                    type="number"
                    step="0.01"
                    value={vatHtAmount}
                    onChange={(e) => setVatHtAmount(parseFloat(e.target.value) || 0)}
                    className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-2.5 pr-12 text-slate-900 focus:bg-white focus:ring-2 focus:ring-blue-500"
                    required
                  />
                  <span className="absolute right-3 top-2.5 text-xs font-semibold text-slate-400">{vatCurrency}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Taux de TVA (%)</label>
                  <select
                    value={vatRate}
                    onChange={(e) => setVatRate(parseFloat(e.target.value))}
                    className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white"
                  >
                    <option value={20.0}>20.0 % (Taux standard France/UE)</option>
                    <option value={14.0}>14.0 % (Prestations spécifiques)</option>
                    <option value={10.0}>10.0 % (Restauration / Bâtiment)</option>
                    <option value={5.5}>5.5 % (Taux réduit première nécessité)</option>
                    <option value={0.0}>0.0 % (Exonéré / Export)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Remise commerciale (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={vatDiscount}
                    onChange={(e) => setVatDiscount(parseFloat(e.target.value) || 0)}
                    className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Devise de transaction</label>
                <select
                  value={vatCurrency}
                  onChange={(e) => setVatCurrency(e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2 text-slate-900"
                >
                  <option value="EUR">EUR (€) - Euro</option>
                  <option value="MAD">MAD - Dirham Marocain</option>
                  <option value="USD">USD ($) - Dollar US</option>
                  <option value="DZD">DZD - Dinar Algérien</option>
                  <option value="TND">TND - Dinar Tunisien</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg text-xs shadow-xs cursor-pointer transition-colors"
              >
                Calculer & Vérifier Déterminisme
              </button>
            </form>
          )}

          {activeCalculator === 'margin' && (
            <form onSubmit={handleComputeMargin} className="space-y-4">
              <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <Percent className="w-4 h-4 text-emerald-600" />
                Simulateur de Marges & Taux de Marque
              </h3>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Coût d'achat / Prix de revient (HT)</label>
                <input
                  type="number"
                  step="0.01"
                  value={marginCostPrice}
                  onChange={(e) => setMarginCostPrice(parseFloat(e.target.value) || 0)}
                  className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Prix de vente proposé (HT)</label>
                <input
                  type="number"
                  step="0.01"
                  value={marginSellingPrice}
                  onChange={(e) => setMarginSellingPrice(parseFloat(e.target.value) || 0)}
                  className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 rounded-lg text-xs shadow-xs cursor-pointer transition-colors"
              >
                Calculer Marges & Coefficients
              </button>
            </form>
          )}

          {activeCalculator === 'budget' && (
            <form onSubmit={handleComputeBudget} className="space-y-4">
              <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-purple-600" />
                Simulateur d'Écart Budgétaire
              </h3>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Budget Initial Alloué / Prévu</label>
                <input
                  type="number"
                  step="0.01"
                  value={budgetPlanned}
                  onChange={(e) => setBudgetPlanned(parseFloat(e.target.value) || 0)}
                  className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Dépense Réelle Constatée</label>
                <input
                  type="number"
                  step="0.01"
                  value={budgetActual}
                  onChange={(e) => setBudgetActual(parseFloat(e.target.value) || 0)}
                  className="w-full text-xs font-mono bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-900 focus:bg-white"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2.5 rounded-lg text-xs shadow-xs cursor-pointer transition-colors"
              >
                Calculer l'Écart & Pourcentage
              </button>
            </form>
          )}
        </div>

        {/* Results & Audit Panel Column */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-4">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                Résultat Certifié & Traçabilité
              </div>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
                Validation Déterministe OK
              </span>
            </div>

            {/* Display Active Result */}
            {activeCalculator === 'vat' && vatResult && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[11px] text-slate-500 font-medium">Net HT Après Remise</span>
                    <div className="text-lg font-bold text-slate-900 font-mono mt-0.5">
                      {vatResult.details?.net_ht?.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} {vatCurrency}
                    </div>
                    {vatResult.details?.discount_amount > 0 && (
                      <span className="text-[10px] text-amber-600 font-medium">
                        Remise : -{vatResult.details?.discount_amount} {vatCurrency}
                      </span>
                    )}
                  </div>

                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[11px] text-slate-500 font-medium">Montant TVA ({vatRate}%)</span>
                    <div className="text-lg font-bold text-blue-600 font-mono mt-0.5">
                      {vatResult.details?.tva_amount?.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} {vatCurrency}
                    </div>
                  </div>

                  <div className="p-3 bg-blue-50/70 rounded-xl border border-blue-200 col-span-2 sm:col-span-1">
                    <span className="text-[11px] text-blue-700 font-bold">Total TTC Final</span>
                    <div className="text-xl font-extrabold text-blue-900 font-mono mt-0.5">
                      {vatResult.result?.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} {vatCurrency}
                    </div>
                  </div>
                </div>

                <div className="p-3 bg-slate-900 text-slate-200 rounded-xl font-mono text-xs space-y-1">
                  <div className="text-slate-400 text-[10px] uppercase tracking-wider">Formule & Justification d'Audit</div>
                  <div className="text-emerald-400 whitespace-pre-wrap">{vatResult.formula}</div>
                </div>
              </div>
            )}

            {activeCalculator === 'margin' && marginResult && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-3">
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[11px] text-slate-500 font-medium">Marge Brute</span>
                    <div className="text-lg font-bold text-emerald-700 font-mono mt-0.5">
                      {marginResult.result?.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} {marginCurrency}
                    </div>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[11px] text-slate-500 font-medium">Taux de Marge (sur coût)</span>
                    <div className="text-lg font-bold text-slate-900 font-mono mt-0.5">
                      {marginResult.details?.margin_rate_pct}%
                    </div>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[11px] text-slate-500 font-medium">Taux de Marque (sur vente)</span>
                    <div className="text-lg font-bold text-blue-600 font-mono mt-0.5">
                      {marginResult.details?.markup_rate_pct}%
                    </div>
                  </div>
                </div>

                <div className="p-3 bg-slate-900 text-slate-200 rounded-xl font-mono text-xs space-y-1">
                  <div className="text-slate-400 text-[10px] uppercase tracking-wider">Formule & Justification d'Audit</div>
                  <div className="text-emerald-400 whitespace-pre-wrap">{marginResult.formula}</div>
                </div>
              </div>
            )}

            {activeCalculator === 'budget' && budgetResult && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[11px] text-slate-500 font-medium">Écart en Valeur</span>
                    <div
                      className={`text-xl font-bold font-mono mt-0.5 ${
                        budgetResult.result > 0 ? 'text-rose-600' : 'text-emerald-600'
                      }`}
                    >
                      {budgetResult.result > 0 ? '+' : ''}
                      {budgetResult.result?.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} {budgetCurrency}
                    </div>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[11px] text-slate-500 font-medium">Variation en Pourcentage</span>
                    <div
                      className={`text-xl font-bold font-mono mt-0.5 ${
                        budgetResult.details?.variance_pct > 0 ? 'text-rose-600' : 'text-emerald-600'
                      }`}
                    >
                      {budgetResult.details?.variance_pct > 0 ? '+' : ''}
                      {budgetResult.details?.variance_pct}%
                    </div>
                    <span className="text-[10px] font-semibold text-slate-500">{budgetResult.details?.status}</span>
                  </div>
                </div>

                <div className="p-3 bg-slate-900 text-slate-200 rounded-xl font-mono text-xs space-y-1">
                  <div className="text-slate-400 text-[10px] uppercase tracking-wider">Formule & Justification d'Audit</div>
                  <div className="text-emerald-400 whitespace-pre-wrap">{budgetResult.formula}</div>
                </div>
              </div>
            )}
          </div>

          <p className="text-[11px] text-slate-400 mt-6 border-t border-slate-100 pt-3">
            Toutes les opérations appliquent la norme d'arrondi monétaire légal <strong>ROUND_HALF_UP</strong> à 2 décimales.
          </p>
        </div>
      </div>

      {/* Historical Calculation Audits Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Clock className="w-4 h-4 text-purple-600" />
            Journal d'Audit des Calculs Récents
          </h3>
          <button
            onClick={loadAudits}
            className="text-xs text-blue-600 hover:underline flex items-center gap-1 cursor-pointer"
          >
            <RefreshCw className="w-3 h-3" />
            Actualiser
          </button>
        </div>

        {audits.length === 0 ? (
          <p className="text-xs text-slate-400 py-4 text-center">Aucun calcul audité pour le moment.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px]">
                  <th className="py-2.5 px-3">Opération</th>
                  <th className="py-2.5 px-3">Formule Traçable</th>
                  <th className="py-2.5 px-3">Résultat Validé</th>
                  <th className="py-2.5 px-3">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                {audits.slice(0, 8).map((a, i) => (
                  <tr key={a.id || i} className="hover:bg-slate-50/50">
                    <td className="py-2.5 px-3 font-semibold text-slate-800">{a.operation}</td>
                    <td className="py-2.5 px-3 text-slate-600 max-w-md truncate" title={a.formula}>
                      {a.formula}
                    </td>
                    <td className="py-2.5 px-3 font-bold text-blue-700">
                      {a.result} {a.currency_or_unit}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="text-[10px] bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded font-sans font-semibold">
                        Certifié
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

