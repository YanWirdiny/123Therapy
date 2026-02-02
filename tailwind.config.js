// Tailwind CSS configuration for 123Therapy
// This is used with the CDN via tailwind.config object

tailwind.config = {
  theme: {
    extend: {
      colors: {
        'sage': {
          DEFAULT: '#8FAE8B',
          light: '#A8C5A5',
          dark: '#7A9A76',
        },
        'sky-soft': '#A8C5D6',
        'sand': {
          light: '#F5F1EB',
          DEFAULT: '#E8E4DF',
        },
        'warm-white': '#FAF9F6',
        'charcoal': '#3D3D3D',
        'warm-gray': '#6B6B6B',
        'partner-a': '#7EB5A6',
        'partner-b': '#D4A5A5',
        'ai-therapist': '#B8A9C9',
        'crisis': '#E8A598',
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
      },
    },
  },
}
