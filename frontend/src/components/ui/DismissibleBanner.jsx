import { useEffect, useState } from 'react'

function DismissibleBanner({ id, storageKeyPrefix = 'banner', children, className }) {
  const key = `${storageKeyPrefix}:${id}`
  const [isOpen, setIsOpen] = useState(true)

  useEffect(() => {
    try {
      if (window?.localStorage?.getItem(key) === 'hidden') {
        setIsOpen(false)
      }
    } catch (error) {
      console.warn('Banner storage unavailable', error)
    }
  }, [key])

  if (!isOpen) return null

  const handleClose = () => {
    setIsOpen(false)
    try {
      window?.localStorage?.setItem(key, 'hidden')
    } catch (error) {
      console.warn('Banner storage unavailable', error)
    }
  }

  return (
    <div className={className}>
      {typeof children === 'function' ? children({ close: handleClose }) : children}
    </div>
  )
}

export default DismissibleBanner
