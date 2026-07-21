import { create } from 'zustand';
export const useCaseStore = create((set, get) => ({
  selectedCaseId: null,
  disputes: {},
  signoffs: {},

  selectCase: (id) => set({ selectedCaseId: id }),


  flagDispute: (caseId, findingId, reason) =>
    set((state) => ({
      disputes: {
        ...state.disputes,
        [caseId]: {
          ...(state.disputes[caseId] || {}),
          [findingId]: { reason, at: new Date().toISOString() },
        },
      },
    })),

  signOff: (caseId, analystEmail) =>
    set((state) => ({
      signoffs: {
        ...state.signoffs,
        [caseId]: { analyst: analystEmail, at: new Date().toISOString() },
      },
    })),
}));
