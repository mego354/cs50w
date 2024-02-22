const input = document.querySelector('#image_uploads');
const image_label = document.querySelector('#label_upload');
const image_p = document.querySelector('#image_p');
const div = document.querySelector('#form_card');
const input_div = document.querySelector('#image_div');


input.onchange = () => {
    const file = input.files[0];
    const reader = new FileReader();
    if (file) {
        reader.onload = function(e) {
            // Create an image element
            const img = document.createElement('img');
            const link = document.createElement("a");
            link.className = "post_image";
            img.className = "card-img-top";
            
            // Set the image source to the data URL
            img.src = e.target.result;
    
            // Append the image to the preview div
            link.appendChild(img);
            div.appendChild(link);
        };
        // Read the file as a data URL
        reader.readAsDataURL(file);
        image_label.style.display = "none";  
        input_div.style.padding = "0";  
        
    }

};
