import type { ReactNode } from 'react'
export function Modal({ children, onClose }: { children: ReactNode; onClose: () => void }) { return <div className="modal-backdrop" onMouseDown={e => e.target === e.currentTarget && onClose()}><section className="modal" role="dialog" aria-modal="true">{children}</section></div> }
