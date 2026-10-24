import type { ButtonHTMLAttributes } from 'react'
export function Button(props: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'quiet' }) {
  const { variant = 'primary', className = '', ...rest } = props
  return <button {...rest} className={`button button-${variant} ${className}`}/>
}
