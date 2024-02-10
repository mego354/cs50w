document.querySelector('#customer_search').onkeyup = function() {
  const users_div = document.querySelector('#users_search');
  users_div.innerHTML = "";
  if (this.value === "all") {

    let user_li = document.createElement('li');
    user_li.innerHTML = `<a href="/users/">All</a>`;

    users_div.append(user_li);

    // Trigger the transition by adding the 'show' class
      user_li.classList.add('show');
        
    
  
    

  }
  else {
    fetch(`/users_search/${this.value.trim()}`)
    .then(response => response.json())
    .then(users => {
      users.forEach((user, index) => {
        let user_li = document.createElement('li');
        user_li.innerHTML = `<a href="/users/${user.id}">${user.id}. ${user.name}</a>`;
        users_div.append(user_li);
  
        // Trigger the transition by adding the 'show' class
        setTimeout(() => {
          user_li.classList.add('show');
        }, index * 50);  // Set a delay based on the index of the element
      });
    });
  
  }
};
