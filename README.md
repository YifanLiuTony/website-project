# Localhost instructions

# serve locally with PHP:
- php -S localhost:8000
# route internet request with ngrok
- ngrok http 8000

# Sunfly Building Materials Website

This is a complete HTML/CSS/JS conversion of the Figma-exported React website for Sunfly Building Materials (Hong Kong) Corporation Limited.

## Features

- **Multi-language Support**: English (EN), Traditional Chinese (繁), and Simplified Chinese (简)
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Smooth Scrolling**: Seamless navigation between sections
- **Interactive Contact Form**: Fully functional form with validation
- **Mobile Menu**: Collapsible navigation for mobile devices
- **Modern Design**: Using Tailwind CSS for styling

## Files Included

```
website/
├── index.html              # Main HTML file
├── js/
│   ├── translations.js     # All language translations
│   └── main.js            # Main JavaScript functionality
├── assets/
│   ├── project1.png       # Macau Galaxy project image
│   └── project1-info.png  # Project information image
└── README.md              # This file
```

## How to Use

1. **Open the Website**: Simply open `index.html` in any modern web browser (Chrome, Firefox, Safari, Edge)

2. **Language Switching**: Click the language buttons (EN / 繁 / 简) in the top-right corner to switch languages

3. **Navigation**: 
   - Use the navigation menu to jump to different sections
   - Click "Get Quote" to scroll to the contact form
   - On mobile, tap the menu icon to access navigation

4. **Contact Form**: Fill out the form in the Contact section to send a message (note: currently shows an alert, but can be integrated with a backend service)

## Customization

### Changing Colors
The website uses Tailwind CSS. The main brand color is orange-500. To change colors, modify the `tailwind.config` section in the `<head>` of `index.html`.

### Adding/Modifying Text
All text content is stored in `js/translations.js`. Edit the translations for all three languages (EN, 繁, 简) to keep consistency.

### Adding Images
Place new images in the `assets/` folder and reference them using `assets/your-image.png` in the HTML.

## Technical Details

- **CSS Framework**: Tailwind CSS via CDN
- **Icons**: Inline SVG icons (Heroicons style)
- **JavaScript**: Vanilla JavaScript (no frameworks)
- **Responsive**: Mobile-first design with breakpoints at 768px (md) and 1024px (lg)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Deployment

To deploy this website:

1. Upload all files to your web server
2. Make sure the folder structure is maintained
3. The website will work immediately - no build process required!

For production use, consider:
- Integrating the contact form with a backend API
- Adding analytics tracking
- Optimizing images for web
- Setting up a proper CDN for assets

## Contact

Sunfly Building Materials (Hong Kong) Corporation Limited
- Phone: +852 5644 1916
- Email: info@sunfly.com.hk
- Sales: sales@sunfly.com.hk

---

**Note**: This website has been converted from a React/TypeScript Figma export to vanilla HTML/CSS/JS while maintaining the exact design, layout, and functionality.
