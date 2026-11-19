document.documentElement.classList.add('has-mobile-menu');

document.querySelectorAll('header nav').forEach((navigation, index) => {
    const header = navigation.closest('header');
    if (!header) return;

    navigation.id ||= `site-navigation-${index}`;
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'mobile-menu-toggle';
    toggle.setAttribute('aria-controls', navigation.id);
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation menu');

    const icon = document.createElement('span');
    icon.setAttribute('aria-hidden', 'true');
    icon.textContent = '\u2630';
    const label = document.createElement('span');
    label.textContent = 'Menu';
    toggle.append(icon, label);
    navigation.before(toggle);

    header.querySelector('a[href="/quiz/"]')?.classList.add('mobile-menu-primary-action');

    const closeMenu = () => {
        header.classList.remove('mobile-menu-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.setAttribute('aria-label', 'Open navigation menu');
    };

    toggle.addEventListener('click', () => {
        const isOpen = header.classList.toggle('mobile-menu-open');
        toggle.setAttribute('aria-expanded', String(isOpen));
        toggle.setAttribute('aria-label', isOpen ? 'Close navigation menu' : 'Open navigation menu');
    });
    navigation.addEventListener('click', event => {
        if (event.target instanceof Element && event.target.closest('a')) closeMenu();
    });
    document.addEventListener('click', event => {
        if (!header.contains(event.target)) closeMenu();
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && header.classList.contains('mobile-menu-open')) {
            closeMenu();
            toggle.focus();
        }
    });
});