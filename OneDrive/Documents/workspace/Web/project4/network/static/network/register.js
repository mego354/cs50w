const input = document.querySelector('#profile_pic');
const text = document.querySelector('#profile_pic_label');
const label = document.querySelector('#img_label');
input.onchange = () => {
    file_name = input.files[0].name
    text.innerHTML = file_name
    label.innerHTML = "uploaded successfuly!"

}
