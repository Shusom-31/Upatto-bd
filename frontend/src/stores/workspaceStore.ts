import { useSyncExternalStore } from 'react'
import type { Dataset, Profile, Session } from '../types'

type State = { session: Session | null; dataset: Dataset | null; profile: Profile | null }
let state: State = { session: null, dataset: null, profile: null }
const listeners = new Set<() => void>()
function subscribe(listener: () => void) { listeners.add(listener); return () => listeners.delete(listener) }
function update(next: Partial<State>) { state = { ...state, ...next }; listeners.forEach(listener => listener()) }
export const workspaceStore = { setSession: (session: Session | null) => update({ session }), setDataset: (dataset: Dataset | null) => update({ dataset }), setProfile: (profile: Profile | null) => update({ profile }), clear: () => update({ session: null, dataset: null, profile: null }) }
export function useWorkspaceStore() { return useSyncExternalStore(subscribe, () => state, () => state) }
