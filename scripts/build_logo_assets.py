import os
import base64

def generate_logo_assets():
    assets_dir = os.path.abspath('assets')
    transparent_png_path = os.path.join(assets_dir, 'mr_logo_transparent.png')
    
    if not os.path.exists(transparent_png_path):
        raise FileNotFoundError(f"Missing master asset: {transparent_png_path}")
        
    with open(transparent_png_path, 'rb') as f:
        png_b64 = base64.b64encode(f.read()).decode('utf-8')

    logo_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1600" width="100%" height="100%" class="mandroos-master-logo-svg">
  <defs>
    <!-- CSS Animations for Floating, Orbital Pulse, and Glint Sweep -->
    <style>
      @keyframes mandroos-float-motion {{
        0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-16px) rotate(0.7deg); }}
      }}
      @keyframes mandroos-orbital-pulse {{
        0%, 100% {{
          filter: drop-shadow(0 0 24px rgba(0, 245, 212, 0.55)) drop-shadow(0 0 45px rgba(244, 63, 94, 0.45));
        }}
        50% {{
          filter: drop-shadow(0 0 40px rgba(0, 245, 212, 0.85)) drop-shadow(0 0 68px rgba(244, 63, 94, 0.70)) drop-shadow(0 0 25px rgba(255, 255, 255, 0.45));
        }}
      }}
      @keyframes glint-sheen-sweep {{
        0% {{ transform: translateX(-650px) skewX(-25deg); opacity: 0; }}
        12% {{ opacity: 0.95; }}
        42% {{ transform: translateX(650px) skewX(-25deg); opacity: 0.95; }}
        55%, 100% {{ transform: translateX(950px) skewX(-25deg); opacity: 0; }}
      }}
      .mandroos-animated-emblem {{
        transform-origin: center center;
        animation: mandroos-float-motion 5s ease-in-out infinite, mandroos-orbital-pulse 4.2s ease-in-out infinite;
        will-change: transform, filter;
      }}
      .mandroos-animated-glint {{
        animation: glint-sheen-sweep 4.5s ease-in-out infinite;
        transform-origin: center center;
      }}
    </style>

    <!-- Intense White Frame Glow Filter -->
    <filter id="whiteFrameGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#FFFFFF" flood-opacity="0.95"/>
      <feDropShadow dx="0" dy="0" stdDeviation="16" flood-color="#FFFFFF" flood-opacity="0.65"/>
      <feDropShadow dx="0" dy="0" stdDeviation="28" flood-color="#38BDF8" flood-opacity="0.5"/>
    </filter>

    <!-- Deep Pitch-Black Sunglasses Lens Gradient -->
    <linearGradient id="sunglassesLens" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#111728"/>
      <stop offset="28%" stop-color="#05070E"/>
      <stop offset="85%" stop-color="#020306"/>
      <stop offset="100%" stop-color="#000002"/>
    </linearGradient>

    <!-- ClipPath to restrict the Specular Glint Sheen strictly to the Glass Lenses -->
    <clipPath id="sunglassesLensClip">
      <!-- Left Lens Inner Area -->
      <path d="M 470 435 
               C 560 425, 675 425, 725 435 
               C 742 445, 746 470, 736 510 
               C 720 575, 675 630, 595 635 
               C 515 640, 465 585, 450 525 
               C 440 470, 448 445, 470 435 Z"/>
      <!-- Right Lens Inner Area -->
      <path d="M 855 435 
               C 905 425, 1020 425, 1110 435 
               C 1132 445, 1140 470, 1130 525 
               C 1115 585, 1065 640, 985 635 
               C 905 630, 860 575, 844 510 
               C 834 470, 838 445, 855 435 Z"/>
    </clipPath>

    <!-- Animated Glint Sheen Gradient -->
    <linearGradient id="glintGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="transparent"/>
      <stop offset="38%" stop-color="transparent"/>
      <stop offset="46%" stop-color="rgba(255, 255, 255, 0.95)"/>
      <stop offset="50%" stop-color="rgba(56, 189, 248, 1)"/>
      <stop offset="54%" stop-color="rgba(255, 255, 255, 0.95)"/>
      <stop offset="62%" stop-color="transparent"/>
      <stop offset="72%" stop-color="transparent"/>
      <stop offset="76%" stop-color="rgba(255, 255, 255, 0.55)"/>
      <stop offset="80%" stop-color="transparent"/>
    </linearGradient>
  </defs>

  <g class="mandroos-animated-emblem">
    <!-- BASE MANDOROS LOGO: 100% UNTOUCHED, IDENTICAL PROPORTIONS, COLORS & GEOMETRY -->
    <g id="mandoros-base-logo">
      <image href="data:image/png;base64,{png_b64}" x="0" y="0" width="1600" height="1600" preserveAspectRatio="xMidYMid meet"/>
    </g>

    <!-- BOLD BLACK SUNGLASSES WITH HIGH-CONTRAST WHITE FRAME OVERLAY -->
    <g id="mandoros-blind-sunglasses">
      <!-- White Frame Temples / Side-arms hooking outward to M vertical bars -->
      <path d="M 450 455 C 410 450, 375 448, 345 452" 
            fill="none" stroke="#FFFFFF" stroke-width="24" stroke-linecap="round" filter="url(#whiteFrameGlow)"/>
      <path d="M 1130 455 C 1170 450, 1205 448, 1235 452" 
            fill="none" stroke="#FFFFFF" stroke-width="24" stroke-linecap="round" filter="url(#whiteFrameGlow)"/>

      <!-- Double Top Brow Bar & Nose Bridge -->
      <path d="M 710 430 Q 790 405 870 430" 
            fill="none" stroke="#FFFFFF" stroke-width="18" stroke-linecap="round" filter="url(#whiteFrameGlow)"/>
      <path d="M 720 465 Q 790 440 860 465" 
            fill="none" stroke="#FFFFFF" stroke-width="28" stroke-linecap="round" filter="url(#whiteFrameGlow)"/>

      <!-- LEFT LENS & BOLD WHITE FRAME -->
      <path d="M 470 435 
               C 560 425, 675 425, 725 435 
               C 742 445, 746 470, 736 510 
               C 720 575, 675 630, 595 635 
               C 515 640, 465 585, 450 525 
               C 440 470, 448 445, 470 435 Z" 
            fill="url(#sunglassesLens)" 
            stroke="#FFFFFF" 
            stroke-width="28" 
            stroke-linejoin="round" 
            filter="url(#whiteFrameGlow)"/>

      <!-- RIGHT LENS & BOLD WHITE FRAME -->
      <path d="M 855 435 
               C 905 425, 1020 425, 1110 435 
               C 1132 445, 1140 470, 1130 525 
               C 1115 585, 1065 640, 985 635 
               C 905 630, 860 575, 844 510 
               C 834 470, 838 445, 855 435 Z" 
            fill="url(#sunglassesLens)" 
            stroke="#FFFFFF" 
            stroke-width="28" 
            stroke-linejoin="round" 
            filter="url(#whiteFrameGlow)"/>

      <!-- ANIMATED SPECULAR GLINT SHEEN SWEEPING ACROSS BOTH LENSES -->
      <g clip-path="url(#sunglassesLensClip)">
        <rect class="mandroos-animated-glint" x="300" y="360" width="1000" height="340" 
              fill="url(#glintGradient)" style="mix-blend-mode: screen;"/>
      </g>

      <!-- Corner Rivet Studs (Classic Wayfarer Style) -->
      <circle cx="462" cy="446" r="6.5" fill="#0B0F19" stroke="#FFFFFF" stroke-width="3.5"/>
      <circle cx="1118" cy="446" r="6.5" fill="#0B0F19" stroke="#FFFFFF" stroke-width="3.5"/>

      <!-- Inner Bridge Accent Studs -->
      <circle cx="730" cy="452" r="4.5" fill="#FFFFFF"/>
      <circle cx="850" cy="452" r="4.5" fill="#FFFFFF"/>

      <!-- Specular Highlight Lines along Frame Edges -->
      <path d="M 485 430 L 710 430" stroke="rgba(255,255,255,0.95)" stroke-width="6" stroke-linecap="round"/>
      <path d="M 870 430 L 1095 430" stroke="rgba(255,255,255,0.95)" stroke-width="6" stroke-linecap="round"/>
    </g>
  </g>
</svg>'''

    # Write logo.svg
    with open('logo.svg', 'w', encoding='utf-8') as f:
        f.write(logo_svg)
    print("Successfully wrote logo.svg")

    # Generate optimized favicon.svg (compact viewBox)
    favicon_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1600" width="32" height="32">
  <defs>
    <filter id="favGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="15" flood-color="#FFFFFF" flood-opacity="0.9"/>
      <feDropShadow dx="0" dy="0" stdDeviation="30" flood-color="#38BDF8" flood-opacity="0.6"/>
    </filter>
    <linearGradient id="favLens" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0c101c"/>
      <stop offset="50%" stop-color="#05070E"/>
      <stop offset="100%" stop-color="#000000"/>
    </linearGradient>
  </defs>
  <image href="data:image/png;base64,{png_b64}" x="0" y="0" width="1600" height="1600"/>
  <g filter="url(#favGlow)">
    <path d="M 450 455 C 410 450, 375 448, 345 452" fill="none" stroke="#FFFFFF" stroke-width="26" stroke-linecap="round"/>
    <path d="M 1130 455 C 1170 450, 1205 448, 1235 452" fill="none" stroke="#FFFFFF" stroke-width="26" stroke-linecap="round"/>
    <path d="M 710 430 Q 790 405 870 430" fill="none" stroke="#FFFFFF" stroke-width="20" stroke-linecap="round"/>
    <path d="M 720 465 Q 790 440 860 465" fill="none" stroke="#FFFFFF" stroke-width="32" stroke-linecap="round"/>
    <path d="M 470 435 C 560 425, 675 425, 725 435 C 742 445, 746 470, 736 510 C 720 575, 675 630, 595 635 C 515 640, 465 585, 450 525 C 440 470, 448 445, 470 435 Z" fill="url(#favLens)" stroke="#FFFFFF" stroke-width="32" stroke-linejoin="round"/>
    <path d="M 855 435 C 905 425, 1020 425, 1110 435 C 1132 445, 1140 470, 1130 525 C 1115 585, 1065 640, 985 635 C 905 630, 860 575, 844 510 C 834 470, 838 445, 855 435 Z" fill="url(#favLens)" stroke="#FFFFFF" stroke-width="32" stroke-linejoin="round"/>
    <!-- Specular glint streak -->
    <path d="M 520 445 L 565 445 L 480 600 L 450 600 Z" fill="rgba(255,255,255,0.7)"/>
    <path d="M 905 445 L 950 445 L 865 600 L 835 600 Z" fill="rgba(255,255,255,0.7)"/>
  </g>
</svg>'''

    with open('favicon.svg', 'w', encoding='utf-8') as f:
        f.write(favicon_svg)
    print("Successfully wrote favicon.svg")

if __name__ == '__main__':
    generate_logo_assets()
