function moderationModal(option, postID)
{
    option = option.toLowerCase()

    let text = "";

    if(option == "delete")
    {
        text = "Are you sure you want to delete this post?\nIt may not be recoverable."
    }

    document.getElementsByClassName('modal-body')[0].innerText = text;
    document.querySelectorAll('.modal-footer > a')[0].setAttribute('href', "../" + postID +  '/delete');
}