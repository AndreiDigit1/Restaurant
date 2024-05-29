        fetch("/menu_route")
            .then(response => response.json())
            .then(data => {
                const menuContainer = document.querySelector('.menu-container');

                data.sortimente.forEach(category => {
                    const categoryDiv = document.createElement('div');
                    categoryDiv.classList.add('category');

                    const categoryTitle = document.createElement('div');
                    categoryTitle.classList.add('category-title');
                    categoryTitle.textContent = category.nume.toUpperCase();
                    categoryDiv.appendChild(categoryTitle);

                    category.retete.forEach(item => {
                        const itemDiv = document.createElement('div');
                        itemDiv.classList.add('item');

                        const itemName = document.createElement('div');
                        itemName.classList.add('item-name');
                        itemName.textContent = item.nume;
                        itemDiv.appendChild(itemName);

                        const itemPrice = document.createElement('div');
                        itemPrice.classList.add('item-price');
                        itemPrice.textContent = item.pret + ' RON';
                        itemDiv.appendChild(itemPrice);

                        categoryDiv.appendChild(itemDiv);
                    });

                    menuContainer.appendChild(categoryDiv);
                });
            })
            .catch(error => console.error('A apărut o eroare:', error));
