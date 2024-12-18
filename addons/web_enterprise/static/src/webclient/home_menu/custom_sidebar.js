
let openMainMenu = null;

console.log("...................>",document.readyState)
function sidebar_open() {
    
    // document.getElementById("mySidebar").style.display = "block";
    // fetchMenuItems();

    var sidebar = document.getElementById("mySidebar");
    if (sidebar) {
        sidebar.style.display = "block";
        fetchMenuItems();
    } else {
        console.error("Sidebar element not found");
    }
}

function sidebar_close() {
    // document.getElementById("mySidebar").style.display = "none";
    var sidebar = document.getElementById("mySidebar");
        if (sidebar) {
            sidebar.style.display = "none";
        } else {
            console.error("Sidebar element not found");
        }
}


function fetchMenuItems() {
    fetch('/get/menu/items')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(menuItems => {
            const menuContainer = document.getElementById("menuItems");
            const logoContainer = document.getElementById("logoContainer");

            if (!menuContainer) {
                console.error('Menu container not found');
                return;
            }
            if (!logoContainer) {
                console.error('Logo container not found');
                return;
            }

            menuContainer.innerHTML = ''; 
            logoContainer.innerHTML = ''; 

            menuItems.forEach(item => {
                // Create main menu item
                const mainMenuDiv = document.createElement('div');
                mainMenuDiv.className = 'main-menu-item';

                const mainMenuTitle = document.createElement('div');
                mainMenuTitle.className = 'main-menu-title';

                const logoImginside = document.createElement('img');
                logoImginside.src = item.image_url;
                logoImginside.alt = item.main_menu;
                logoImginside.className = 'main-menu-logo-inside';
                mainMenuTitle.appendChild(logoImginside);

                const titleText = document.createElement('h3');
                titleText.textContent = item.main_menu;
                mainMenuTitle.appendChild(titleText);

                const arrowDown = document.createElement('span');
                arrowDown.className = 'arrow-down';
                mainMenuTitle.appendChild(arrowDown);

                mainMenuDiv.appendChild(mainMenuTitle);

                const logoImg = document.createElement('img');
                logoImg.src = item.image_url;
                logoImg.alt = item.main_menu;
                logoImg.className = 'main-menu-logo';
                logoContainer.appendChild(logoImg);

                // Create submenu items container
                const submenuList = document.createElement('ul');
                submenuList.className = 'submenu-list';
                submenuList.style.display = 'none';

                item.submenus.forEach(submenu => {
                    const submenuItem = document.createElement('li');
                    submenuItem.className = 'submenu-item';

                    const submenuLink = document.createElement('a');
                    submenuLink.href = submenu.submenu_link;
                    submenuLink.textContent = submenu.submenu_name;
                    submenuLink.className = 'submenu-link';

                    // Add submenu logo
                    const submenuLogo = document.createElement('img');
                    submenuLogo.src = submenu.image_url;
                    submenuLogo.alt = submenu.submenu_name;
                    submenuLogo.className = 'submenu-logo';

                    submenuItem.appendChild(submenuLogo);
                    submenuItem.appendChild(submenuLink);
                    submenuList.appendChild(submenuItem);
                });

                mainMenuDiv.appendChild(submenuList);
                menuContainer.appendChild(mainMenuDiv);

                // Add click event to toggle submenus
                mainMenuTitle.addEventListener('click', () => {
                    // Close previously opened main menu
                    if (openMainMenu && openMainMenu !== mainMenuDiv) {
                        const previousSubmenuList = openMainMenu.querySelector('.submenu-list');
                        previousSubmenuList.style.display = 'none';
                    }
                    // Toggle current main menu
                    if (submenuList.style.display === 'none') {
                        submenuList.style.display = 'block';
                        openMainMenu = mainMenuDiv;
                    } else {
                        submenuList.style.display = 'none';
                        openMainMenu = null;
                    }
                });

            });
        })
        .catch(error => {
            console.error('Failed to fetch menu items:', error);
        });
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("----------------Open Function----------->>>>>>>>>..")
    setTimeout(() => {
        sidebar_open();
        console.log("----------------opened----------->>>>>>>>>..")
    }, 500);
});

document.addEventListener('DOMContentLoaded', () => {
    console.log("----------------Close Function----------->>>>>>>>>..")
    setTimeout(() => {
        sidebar_close();
        console.log("----------------closed----------->>>>>>>>>..")
    }, 600); 
});

