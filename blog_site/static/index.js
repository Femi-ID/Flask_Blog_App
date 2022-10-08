function like(postId){
    console.log(postId)
    const likeCount = document.getElementById(`likes-count-${postId}`)
    const likeButton = document.getElementById(`like-Button-${postId}`)
    const likeButton2 = document.getElementById(`like-regularButton-${postId}`)
    //const likeButtonz = document.getElementsByClassName(`like-icon`)

    fetch(`/like_post/${postId}`, {method:"POST"})
    .then((res) => res.json())
    .then((data) => {
    console.log(data)
    likeCount.innerHTML = data['likes'];
    //likeButton.className = "fas fa-thumbs-up"


    if (data['liked'] === true) {
    likeButton.className = "fa-sharp fa-solid fa-heart"}
//    likeButton.innerHTML = 'LIKED'
    else {
    likeButton.className = "fa-regular fa-heart"}
//    likeButton.innerHTML = 'unLIKED'
    });

//    if (data['liked'] === true) {
//    likeButtonz.className = "fas fa-thumbs-up"}
//    else {
//    likeButtonz.className = "far fa-thumbs-up"}
//    });

    //console.log(likeCount.value)
}

