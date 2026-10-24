import { useEffect, useState } from 'react'
export function useNotice(timeout = 4000) { const [notice, setNotice] = useState(''); useEffect(() => { if (!notice) return; const timer = window.setTimeout(() => setNotice(''), timeout); return () => window.clearTimeout(timer) }, [notice, timeout]); return { notice, showNotice: setNotice, clearNotice: () => setNotice('') } }
