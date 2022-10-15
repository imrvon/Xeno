// Password Toggle
function ToggleFunction() {
    let password = document.getElementById('user-pw')
    let hide = document.getElementById('hide')
    let show = document.getElementById('show')

    if(password.type === 'password') {
        password.type = 'text';
        show.style.display = 'block'
        hide.style.display = 'none'
    } else {
        password.type = 'password';
        show.style.display = 'none'
        hide.style.display = 'block'
    }
}

