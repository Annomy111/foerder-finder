function Icon({ icon: IconComponent, size = 20, className = '', strokeWidth = 1.75 }) {
  if (!IconComponent) return null
  return <IconComponent size={size} strokeWidth={strokeWidth} className={className} aria-hidden="true" />
}

export default Icon
