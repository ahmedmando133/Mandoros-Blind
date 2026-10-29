/**
 * MANDOROS™ • Meta-Analysis Network for Data, Outcomes & Research Optimization Synthesis
 * Tier-1 Global Flagship GSAP Motion Architecture (Adidas × Apple/Samsung × Meta Standard)
 * Zero-Server-Footprint • Pure GPU Acceleration • 60fps Butter-Smooth Interaction
 */

(function (window) {
  'use strict';

  // State guards
  let isInitialized = false;
  let isHeroAnimated = false;
  let isPipelineAnimated = false;
  let isBentoAnimated = false;
  let isTopBarAnimated = false;
  const animatedKpiElements = new WeakSet();

  // Accessibility: prefers-reduced-motion check
  function isReducedMotion() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  // Safe registration of GSAP Core & Official Plugins
  let pluginWaitAttempts = 0;
  function registerGsapPlugins() {
    if (typeof window.gsap === 'undefined') {
      pluginWaitAttempts++;
      return false;
    }
    // Give external CDN plugins up to 1.5s (30 * 50ms) to finish downloading
    const hasScrollTrigger = typeof window.ScrollTrigger !== 'undefined';
    const hasTextPlugin = typeof window.TextPlugin !== 'undefined';
    if ((!hasScrollTrigger || !hasTextPlugin) && pluginWaitAttempts < 30) {
      pluginWaitAttempts++;
      return false;
    }
    try {
      if (hasScrollTrigger && !(window.gsap.plugins && window.gsap.plugins.scrollTrigger)) {
        window.gsap.registerPlugin(window.ScrollTrigger);
      }
      if (hasTextPlugin && !(window.gsap.plugins && window.gsap.plugins.text)) {
        window.gsap.registerPlugin(window.TextPlugin);
      }
      if (typeof window.Flip !== 'undefined' && !(window.gsap.plugins && window.gsap.plugins.flip)) {
        window.gsap.registerPlugin(window.Flip);
      }
    } catch (e) {
      console.warn('[MANDOROS GSAP] Plugin registration warning:', e);
    }
    return true;
  }

  // =========================================================================
  // 1. CHOREOGRAPHED HERO & M LOGO MASTER TIMELINE (gsap.timeline())
  // =========================================================================
  function initHeroMasterTimeline() {
    if (isHeroAnimated || isReducedMotion()) return;
    if (typeof window.gsap === 'undefined') return;

    const emblem = document.querySelector('.emblem-wrapper svg, .mandoros-m-logo-svg');
    const heroTitle = document.querySelector('.mandoros-hero-title');
    const subtitle = document.querySelector('.mandoros-subtitle');
    const badgeStrip = document.querySelector('.hero-spec-strip');
    const statusPill = document.querySelector('.hero-system-status');

    if (emblem || heroTitle) {
      isHeroAnimated = true;

      const heroTl = window.gsap.timeline({ defaults: { ease: 'power4.out' } });

      // Step 1: Geometric M Logo scales and rotates in with brushed-titanium sheen
      if (emblem) {
        emblem.style.willChange = 'transform, opacity, filter';
        heroTl.fromTo(emblem,
          { scale: 0.4, rotationY: -90, opacity: 0 },
          { scale: 1, rotationY: 0, opacity: 1, duration: 1.1, ease: 'expo.out' }
        );

        // Infinite 3D metallic levitation
        window.gsap.to(emblem, {
          y: -6,
          duration: 3.0,
          repeat: -1,
          yoyo: true,
          ease: 'sine.inOut'
        });
      }

      // Step 2: System Status Pill Entrance
      if (statusPill) {
        heroTl.from(statusPill, {
          y: -15,
          opacity: 0,
          duration: 0.6,
          ease: 'power3.out'
        }, '-=0.6');
      }

      // Step 3: Split-word kinetic reveal of MANDOROS™
      if (heroTitle) {
        heroTitle.style.willChange = 'transform, opacity';
        heroTl.from(heroTitle, {
          y: 35,
          opacity: 0,
          duration: 0.9,
          ease: 'power4.out',
          clearProps: 'all'
        }, '-=0.5');
      }

      // Step 4: TextPlugin live decode / type-in for Acronym Subtitle
      if (subtitle) {
        const fullText = subtitle.getAttribute('data-full-text') || subtitle.innerText.trim();
        subtitle.setAttribute('data-full-text', fullText);
        subtitle.style.willChange = 'opacity';
        
        if (typeof window.TextPlugin !== 'undefined') {
          heroTl.fromTo(subtitle, 
            { opacity: 0, y: 10 },
            { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out', clearProps: 'all' },
            0.25
          );
        } else {
          heroTl.from(subtitle, {
            y: 15,
            opacity: 0,
            duration: 0.7,
            clearProps: 'all'
          }, 0.25);
        }
      }

      // Step 4b: Glassy Creator & Academic Affiliation Banner Entrance (Concurrent with Hero)
      const creatorBar = document.querySelector('.mandoros-academic-creator-bar');
      if (creatorBar) {
        heroTl.from(creatorBar, {
          y: 15,
          duration: 0.5,
          ease: 'power3.out',
          clearProps: 'all'
        }, 0.1);
      }

      // Step 5: High-density clinical metadata strip reveal
      if (badgeStrip) {
        heroTl.from(badgeStrip.children, {
          y: 12,
          opacity: 0,
          stagger: 0.06,
          duration: 0.5,
          ease: 'power2.out',
          clearProps: 'all'
        }, '-=0.4');
      }
    }
  }

  // =========================================================================
  // 2. 8-NODE M-A-N-D-O-R-O-S KINETIC PIPELINE & TRAVELING LASER PULSE
  // =========================================================================
  function initPipelineStrip() {
    if (isPipelineAnimated || isReducedMotion()) return;
    if (typeof window.gsap === 'undefined') return;

    const strip = document.querySelector('.mandoros-pipeline-strip');
    const nodes = document.querySelectorAll('.mandoros-pipeline-strip .pipeline-node');
    const laserPath = document.querySelector('.pipeline-laser-path');

    if (nodes.length > 0) {
      isPipelineAnimated = true;

      // Cascading reveal: stagger: 0.09, y: 35, scale: 0.85, back.out(1.7)
      window.gsap.from(nodes, {
        y: 35,
        scale: 0.85,
        opacity: 0,
        duration: 0.75,
        stagger: 0.09,
        ease: 'back.out(1.7)',
        clearProps: 'all'
      });

      // Animate pipeline chevrons
      const chevrons = document.querySelectorAll('.mandoros-pipeline-strip .pipeline-chevron');
      if (chevrons.length > 0) {
        window.gsap.from(chevrons, {
          opacity: 0,
          scale: 0.5,
          stagger: 0.08,
          duration: 0.5,
          ease: 'power2.out',
          clearProps: 'all'
        });
      }

      // Traveling laser pulse along connector line from M to S
      if (laserPath) {
        window.gsap.to(laserPath, {
          strokeDashoffset: -400,
          repeat: -1,
          duration: 2.5,
          ease: 'none'
        });
      }

      // Magnetic hover physics & 3D tilt on each pipeline node
      nodes.forEach(node => {
        if (node._hasGsapPhysics) return;
        node._hasGsapPhysics = true;
        node.style.willChange = 'transform';

        const quickRotX = window.gsap.quickTo(node, 'rotationX', { duration: 0.25, ease: 'power2.out' });
        const quickRotY = window.gsap.quickTo(node, 'rotationY', { duration: 0.25, ease: 'power2.out' });
        const quickScale = window.gsap.quickTo(node, 'scale', { duration: 0.25, ease: 'power2.out' });

        node.addEventListener('mousemove', (e) => {
          const rect = node.getBoundingClientRect();
          const x = e.clientX - rect.left - rect.width / 2;
          const y = e.clientY - rect.top - rect.height / 2;
          quickRotX(-y * 0.15);
          quickRotY(x * 0.15);
          quickScale(1.06);
        });

        node.addEventListener('mouseleave', () => {
          quickRotX(0);
          quickRotY(0);
          quickScale(1.0);
        });
      });
    }
  }

  // =========================================================================
  // 3. MAGNETIC CURSOR PULL & 3D PERSPECTIVE TILT (gsap.quickTo())
  // =========================================================================
  function initMagneticTiltCards() {
    if (isReducedMotion() || typeof window.gsap === 'undefined') return;

    // Bento cards, Phase cards, Pillar cards, Action buttons
    const targets = document.querySelectorAll(
      '.bento-spotlight-card, .product-phase-card, .academic-pillar-card, .mandoros-kpi-card, .mandoros-magnetic-btn, .extract-btn'
    );

    targets.forEach(el => {
      if (el._hasMagneticTilt) return;
      el._hasMagneticTilt = true;
      el.style.transformStyle = 'preserve-3d';
      el.style.willChange = 'transform';

      const isButton = el.tagName === 'BUTTON' || el.classList.contains('mandoros-magnetic-btn') || el.classList.contains('extract-btn');

      const quickX = isButton ? window.gsap.quickTo(el, 'x', { duration: 0.3, ease: 'power2.out' }) : null;
      const quickY = isButton ? window.gsap.quickTo(el, 'y', { duration: 0.3, ease: 'power2.out' }) : null;
      const quickRotX = window.gsap.quickTo(el, 'rotationX', { duration: 0.25, ease: 'power1.out' });
      const quickRotY = window.gsap.quickTo(el, 'rotationY', { duration: 0.25, ease: 'power1.out' });

      el.addEventListener('mousemove', (e) => {
        const rect = el.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        const cx = rect.width / 2;
        const cy = rect.height / 2;
        const deltaX = mouseX - cx;
        const deltaY = mouseY - cy;

        // Aceternity Spotlight CSS coordinates
        el.style.setProperty('--mouse-x', `${mouseX}px`);
        el.style.setProperty('--mouse-y', `${mouseY}px`);

        // 3D Physical Tilt
        const maxTilt = isButton ? 4 : 7;
        const tiltX = -(deltaY / cy) * maxTilt;
        const tiltY = (deltaX / cx) * maxTilt;
        quickRotX(tiltX);
        quickRotY(tiltY);

        // Magnetic Pull for buttons
        if (isButton && quickX && quickY) {
          quickX(deltaX * 0.22);
          quickY(deltaY * 0.22);
        }
      });

      el.addEventListener('mouseleave', () => {
        quickRotX(0);
        quickRotY(0);
        if (quickX && quickY) {
          quickX(0);
          quickY(0);
        }
      });
    });
  }

  // =========================================================================
  // 4. SCROLLTRIGGER BENTO GRID & SECTION REVEALS
  // =========================================================================
  function initScrollTriggerBentoGrid() {
    if (isBentoAnimated || isReducedMotion()) return;
    if (typeof window.gsap === 'undefined') return;

    const bentoCards = document.querySelectorAll(
      '.bento-spotlight-card, .product-phase-card, .academic-pillar-card'
    );

    if (bentoCards.length > 0) {
      isBentoAnimated = true;

      // Unmistakable ScrollTrigger Reveal with 3D Perspective Lift
      if (typeof window.ScrollTrigger !== 'undefined') {
        window.ScrollTrigger.batch(bentoCards, {
          onEnter: batch => {
            window.gsap.fromTo(batch,
              { y: 45, opacity: 0, scale: 0.96 },
              { y: 0, opacity: 1, scale: 1, duration: 0.85, stagger: 0.1, ease: 'power4.out', clearProps: 'all' }
            );
          },
          start: 'top 88%',
          once: true
        });
      } else {
        window.gsap.from(bentoCards, {
          y: 40,
          opacity: 0,
          stagger: 0.1,
          duration: 0.85,
          ease: 'power4.out',
          clearProps: 'all'
        });
      }
    }
  }

  // =========================================================================
  // 5. FLUID GSAP TAB & STATE TRANSITIONS (Flip / Timeline)
  // =========================================================================
  function initTabTransitions() {
    const tabButtons = document.querySelectorAll(
      '#main-phases-tabs button[role="tab"], #main-phases-tabs .tab-nav > button, #main-phases-tabs .tab-container > button, .sheet-tab-btn, .main-tab-btn'
    );

    tabButtons.forEach(btn => {
      if (btn._hasGsapTabHook) return;
      btn._hasGsapTabHook = true;

      // Subtle GSAP Hover Physics on Tab Buttons
      btn.addEventListener('mouseenter', () => {
        if (!btn.classList.contains('selected') && btn.getAttribute('aria-selected') !== 'true') {
          window.gsap.to(btn, { scale: 1.02, duration: 0.2, ease: 'power2.out' });
        }
      });
      btn.addEventListener('mouseleave', () => {
        window.gsap.to(btn, { scale: 1.0, duration: 0.2, ease: 'power2.out' });
      });

      btn.addEventListener('click', () => {
        window.gsap.fromTo(btn, { scale: 0.97 }, { scale: 1.0, duration: 0.25, ease: 'back.out(2)' });
        setTimeout(() => {
          const activePanel = document.querySelector(
            '#main-phases-tabs div[role="tabpanel"]:not(.hidden):not([style*="display: none"]), #main-phases-tabs .tabitem:not(.hidden):not([style*="display: none"]), .main-tab-panel:not(.hidden), .sheet-tab-panel:not(.hidden)'
          );
          if (activePanel && typeof window.gsap !== 'undefined' && !isReducedMotion()) {
            window.gsap.fromTo(activePanel,
              { opacity: 0, y: 14 },
              { opacity: 1, y: 0, duration: 0.4, ease: 'power3.out', clearProps: 'transform' }
            );
          }
          animateKpiCounters(activePanel || document);
        }, 50);
      });
    });

    // Wrapped Programmatic Navigation Bridge
    if (typeof window.selectMandorosPhase === 'function' && !window.selectMandorosPhase._isGsapWrapped) {
      const origBridge = window.selectMandorosPhase;
      const wrappedBridge = function (idx) {
        origBridge(idx);
        setTimeout(() => {
          const activePanel = document.querySelector(
            '#main-phases-tabs div[role="tabpanel"]:not(.hidden):not([style*="display: none"]), #main-phases-tabs .tabitem:not(.hidden):not([style*="display: none"])'
          );
          if (activePanel && typeof window.gsap !== 'undefined' && !isReducedMotion()) {
            window.gsap.fromTo(activePanel,
              { opacity: 0, y: 14 },
              { opacity: 1, y: 0, duration: 0.4, ease: 'power3.out', clearProps: 'transform' }
            );
          }
          animateKpiCounters(activePanel || document);
        }, 60);
      };
      wrappedBridge._isGsapWrapped = true;
      window.selectMandorosPhase = wrappedBridge;
    }
  }

  // =========================================================================
  // 6. HIGH-SPEED GSAP NUMBER SCRAMBLERS & LIVE VIEWPORT COUNTERS
  // =========================================================================
  function animateKpiCounters(scopeRoot) {
    if (typeof window.gsap === 'undefined' || isReducedMotion()) return;
    const root = scopeRoot || document;

    const candidates = root.querySelectorAll(
      '.mandoros-kpi-val, .mandoros-counter, .glass-card .text-xl.font-extrabold, .bento-metric-val'
    );

    candidates.forEach(el => {
      if (animatedKpiElements.has(el)) return;
      const rawText = (el.dataset.kpiVal || el.innerText || '').trim();
      if (!rawText) return;

      // Matches positive/negative numbers, decimals, and units:
      // Examples: "88", "25s", "99.5%", "-1.74", "91.2%", "84 / 100", "N = 340"
      const match = rawText.match(/^([^\d.-]*)(-?[\d,]+(?:\.\d+)?)(.*)$/);
      if (match) {
        const prefix = match[1] || '';
        const numStr = match[2].replace(/,/g, '');
        const targetVal = parseFloat(numStr);
        const suffix = match[3] || '';

        if (!isNaN(targetVal) && targetVal !== 0) {
          animatedKpiElements.add(el);
          const hasDecimals = numStr.includes('.');
          const decimals = hasDecimals ? (numStr.split('.')[1] || '').length : 0;
          const counterObj = { val: 0 };

          window.gsap.to(counterObj, {
            val: targetVal,
            duration: 1.6,
            ease: 'power2.out',
            onUpdate: function () {
              const formatted = decimals > 0 ? counterObj.val.toFixed(decimals) : Math.round(counterObj.val).toLocaleString();
              el.innerText = `${prefix}${formatted}${suffix}`;
            },
            onComplete: function () {
              el.innerText = rawText;
            }
          });
        }
      }
    });
  }

  // =========================================================================
  // 7. PRISMA 2020 SVG FLOW DIAGRAM ANIMATION
  // =========================================================================
  function animatePrismaFlow(container) {
    if (typeof window.gsap === 'undefined' || isReducedMotion()) return;
    const root = container || document;

    const paths = root.querySelectorAll('.prisma-flow-path');
    if (paths.length > 0) {
      paths.forEach(p => {
        try {
          const len = p.getTotalLength ? p.getTotalLength() : 120;
          window.gsap.fromTo(p,
            { strokeDasharray: len, strokeDashoffset: len },
            { strokeDashoffset: 0, duration: 0.85, ease: 'power2.out', overwrite: 'auto' }
          );
        } catch (e) {}
      });
    }

    const stageCards = root.querySelectorAll('.prisma-stage-card');
    if (stageCards.length > 0) {
      window.gsap.fromTo(stageCards,
        { y: 22, opacity: 0, scale: 0.95 },
        { y: 0, opacity: 1, scale: 1, duration: 0.65, stagger: 0.12, ease: 'back.out(1.5)', clearProps: 'all', overwrite: 'auto' }
      );
    }
  }

  // =========================================================================
  // 8. TOP STATUS BAR & NCBI STATUS ENTRANCE
  // =========================================================================
  function initTopBarAndPillars() {
    if (isTopBarAnimated || isReducedMotion()) return;
    if (typeof window.gsap === 'undefined') return;

    const topBar = document.querySelector('.mandoros-top-mirror-bar');
    const ncbiPillar = document.querySelector('.mandoros-ncbi-pillar-container, .mandoros-ncpi-pillar-container');
    const targets = [topBar, ncbiPillar].filter(Boolean);

    if (targets.length > 0) {
      isTopBarAnimated = true;
      window.gsap.from(targets, {
        y: -25,
        opacity: 0,
        duration: 0.8,
        ease: 'power3.out',
        stagger: 0.1,
        clearProps: 'transform'
      });
    }

    // Hardware LED Pulse on Live Render Production Indicator
    const prodDot = document.querySelector('.mandoros-prod-dot');
    if (prodDot && !prodDot._gsapPulsing) {
      prodDot._gsapPulsing = true;
      window.gsap.to(prodDot, {
        opacity: 0.4,
        scale: 1.35,
        duration: 1.2,
        repeat: -1,
        yoyo: true,
        ease: 'power1.inOut'
      });
    }

    // Interactive Hover & Pulse for 16GB HF Failover Badge (.mandoros-hf-badge)
    const hfBadge = document.querySelector('.mandoros-hf-badge');
    if (hfBadge && !hfBadge._gsapBound) {
      hfBadge._gsapBound = true;
      hfBadge.addEventListener('mouseenter', () => {
        window.gsap.to(hfBadge, { scale: 1.05, duration: 0.25, ease: 'power2.out' });
      });
      hfBadge.addEventListener('mouseleave', () => {
        window.gsap.to(hfBadge, { scale: 1.0, duration: 0.25, ease: 'power2.out' });
      });
    }

    // HL7 FHIR Action Bar entrance and button pulsing (.mandoros-ncbi-fhir-tool)
    const fhirTool = document.querySelector('.mandoros-ncbi-fhir-tool, .mandoros-ncpi-fhir-tool');
    if (fhirTool && !fhirTool._gsapAnimated) {
      fhirTool._gsapAnimated = true;
      window.gsap.from(fhirTool.querySelectorAll('button'), {
        y: 8,
        opacity: 0.6,
        stagger: 0.08,
        duration: 0.5,
        ease: 'power2.out'
      });
    }
  }

  // =========================================================================
  // 9. FAILSAFE VISIBILITY GUARANTEE
  // =========================================================================
  function applyFailsafeVisibility() {
    setTimeout(() => {
      const allCards = document.querySelectorAll(
        '.product-phase-card, .academic-pillar-card, .bento-spotlight-card, .mandoros-top-mirror-bar, .mandoros-hero-title, .pipeline-node'
      );
      allCards.forEach(el => {
        if (window.getComputedStyle(el).opacity === '0') {
          el.style.opacity = '1';
          el.style.transform = 'none';
        }
      });
    }, 2000);
  }

  // =========================================================================
  // 10. MASTER INITIALIZER & DEBOUNCED MUTATION OBSERVER
  // =========================================================================
  function init() {
    if (!registerGsapPlugins()) {
      setTimeout(init, 50);
      return;
    }

    initTopBarAndPillars();
    initHeroMasterTimeline();
    initPipelineStrip();
    initMagneticTiltCards();
    initScrollTriggerBentoGrid();
    initTabTransitions();
    animateKpiCounters(document);
    animatePrismaFlow(document);
    applyFailsafeVisibility();

    if (!isInitialized) {
      isInitialized = true;
      setupMutationObserver();
    }
  }

  let observerDebounce = null;
  function setupMutationObserver() {
    if (!window.MutationObserver) return;

    const observer = new MutationObserver(() => {
      if (observerDebounce) clearTimeout(observerDebounce);
      observerDebounce = setTimeout(() => {
        initTopBarAndPillars();
        initHeroMasterTimeline();
        initPipelineStrip();
        initMagneticTiltCards();
        initScrollTriggerBentoGrid();
        initTabTransitions();
        animateKpiCounters(document);
        animatePrismaFlow(document);
      }, 100);
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  // Expose API to window
  window.mandorosGsap = {
    init: init,
    animateKpiCounters: animateKpiCounters,
    animatePrismaFlow: animatePrismaFlow,
    initTopBarAndPillars: initTopBarAndPillars,
    initHeroMasterTimeline: initHeroMasterTimeline,
    initPipelineStrip: initPipelineStrip,
    initMagneticTiltCards: initMagneticTiltCards,
    initScrollTriggerBentoGrid: initScrollTriggerBentoGrid,
    initTabTransitions: initTabTransitions
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  window.addEventListener('load', init);

})(window);
