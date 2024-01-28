export const navigateToHome = (nutzerrolle, navigateFn) => {
    switch (nutzerrolle) {
    case 'Admin': navigateFn('/admin'); break;
    case 'Netzbetreiber': navigateFn('/netzbetreiber'); break;
    case 'Energieberatende': navigateFn('/energieberatende'); break;
    case 'Solarteure': navigateFn('/solarteure'); break;
    case "Haushalte" : navigateFn('/haushalte'); break;
    }
}