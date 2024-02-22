const posts = document.querySelectorAll('.post');
const posts_text = document.querySelectorAll('.post_text');
const likes_text = document.querySelectorAll('.likes_text');
const likes = document.querySelectorAll('.post_likes');
const [nextBtn, prevBtn] = document.querySelectorAll('#next, #prev');
const page = document.querySelector('#page_no');
const nav = document.querySelector('#navbar');

const limit = 10;
let counter = 0;
let page_no = 1;

nextBtn.addEventListener('click', () => movePosts(-limit));
prevBtn.addEventListener('click', () => movePosts(limit));

function movePosts(offset) {

    counter = Math.min(Math.max(counter + offset, 0), posts.length);
    posts.forEach(post => post.style.display = 'none');
    const start = counter;
    const end = Math.min(counter + limit, posts.length);
    for (let i = start; i < end; i++) {
        posts[i].style.display = 'flex';
    }
    nextBtn.disabled = counter === 0;
    prevBtn.disabled = counter + limit >= posts.length;


    page_no += offset > 0 ? 1 : -1;
    page.innerHTML = page_no === 0 ? "All posts" : `Page${page_no + 1}`;
    if (currentUserId != 'None') {
        console.log(nav.clientHeight)

        page_no > 0 ? window.scrollTo({top: nav.scrollHeight + 207,behavior: 'smooth'}) : window.scrollTo({top: 0,behavior: 'smooth'});
    }
    else {
        page_no > 0 ? window.scrollTo({top: nav.scrollHeight + 17,behavior: 'smooth'}) : window.scrollTo({top: 0,behavior: 'smooth'});
    }
}
movePosts(0);

likes_text.forEach(text => {
    let count_span = document.querySelector(`#likes_count_${text.dataset.postid}`)
    if (parseInt(text.dataset.likes) === 0) {
        text.innerHTML = "Be the first liker !"
        count_span.innerHTML = ""
    }
    else if (parseInt(text.dataset.likes) === 1) {
        text.innerHTML = "like"
    }
    else {
        text.innerHTML = "likes"
    }

})
likes.forEach(like => {
    like.addEventListener('click', () => {
        const icon = document.querySelector(`#icon_${like.dataset.postid}`)
        const count = document.querySelector(`#likes_count_${like.dataset.postid}`)
        const text = document.querySelector(`#likes_text_${like.dataset.postid}`)

        fetch('/like_post/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ postId: like.dataset.postid})
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
    
            if (icon.classList.contains("fa-regular")) {
                icon.classList.remove("fa-regular");
                icon.classList.add("fa-solid");
                icon.classList.add("fa-beat-fade");
                setTimeout(() => {
                icon.classList.remove("fa-beat-fade");

                }, 2150)
                if (count.innerHTML === "") {
                    count.innerHTML = 1;
                }
                else {
                    count.innerHTML = parseInt(count.innerHTML) + 1
                }
                if (parseInt(count.innerHTML) > 1) {
                    text.innerHTML = "likes";
                }
                else if (parseInt(count.innerHTML) === 1) {
                    text.innerHTML = "like";
                }
                
            }
            else {
                icon.classList.add("fa-regular")
                icon.classList.remove("fa-solid")
                count.innerHTML = parseInt(count.innerHTML) - 1
                if (parseInt(count.innerHTML) < 2) {
                    text.innerHTML = "like"
                }
                if (parseInt(count.innerHTML) === 0) {
                    text.innerHTML = "Be the first liker !"
                    count.innerHTML = ""
                }


            }

        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
    
        });


    })
})

posts_text.forEach(div => {
    if (div.dataset.userid === currentUserId) {
        let button = document.createElement('button');
        let icon = document.createElement('i');
        let text = document.createElement('p');
        text.innerHTML = "edit"
        icon.classList.add("fa-solid", "fa-pen-to-square");
        button.className = "post_edit";

        edit_div = document.querySelector(`#edit_${div.dataset.postid}`)
        button.append(icon);
        edit_div.append(text);
        edit_div.append(button);

        edit_div.addEventListener('click', () => toggle_edit_mode(`text_${div.dataset.postid}`, text, div.dataset.postid));

    }
});


function toggle_edit_mode(id, button, postid) {
    if (button.innerHTML === "edit") {
        start_edit_mode(id, button);
    } else {
        end_edit_mode(id, button, postid);
    }
}

function start_edit_mode(id, button) {
    button.innerHTML = "save";
    const inputElement = document.querySelector(`#${id}`);
    const textareaElement = document.createElement("textarea");
    textareaElement.value = inputElement.innerHTML;

    for (const {name, value} of inputElement.attributes) {
        textareaElement.setAttribute(name, value);
    }
    textareaElement.classList.add("post_textarea");
    textareaElement.rows = Math.round(textareaElement.value.length / 60);

    inputElement.parentNode.replaceChild(textareaElement, inputElement);
}

function end_edit_mode(id, button, postId) {
    const textareaElement = document.querySelector(`#${id}`);
    const newText = textareaElement.value;

    fetch('/update_post/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ postId: postId, newText: newText })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        button.innerHTML = "edit";
        const inputElement = document.createElement("p");
        inputElement.innerHTML = newText;

        for (const { name, value } of textareaElement.attributes) {
            inputElement.setAttribute(name, value);
        }

        textareaElement.parentNode.replaceChild(inputElement, textareaElement);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);

    });



}

