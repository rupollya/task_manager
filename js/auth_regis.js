function checkLogin(event) {
    var login = document.getElementById("login").value;
    var password = document.getElementById("password").value;
    var loginInput = document.getElementById("login");
    var passwordInput = document.getElementById("password");

    if (login.length < 1) {
        loginInput.classList.add('is-invalid');
        loginInput.classList.remove('is-valid');
    } else {
        loginInput.classList.remove('is-invalid');
        loginInput.classList.add('is-valid');
    }

    if (password.length < 8) {
        passwordInput.classList.add('is-invalid');
        passwordInput.classList.remove('is-valid');
    } else {
        passwordInput.classList.remove('is-invalid');
        passwordInput.classList.add('is-valid');
    }

    if (login.length > 1 && password.length >= 8) {
        var zapros = new XMLHttpRequest();
        zapros.open("POST", "/auth", true);
        zapros.setRequestHeader("Content-Type", "application/json");

        zapros.onload = function () {
            if (zapros.status === 200) {
                var response = JSON.parse(zapros.responseText);
                if (response.access_token) {
                    //сохраняем токен в куки
                    document.cookie = "access_token=" + response.access_token + "; path=/; max-age=3600";
                    //и в локал сторадж
                    localStorage.setItem('access_token', response.access_token);
                    window.location.href = "/storage.html";
                } else {
                    console.error('Токен доступа не получен:', response);
                }
            } else {
                try {
                    var errorResponse = JSON.parse(zapros.responseText);
                    if (errorResponse.detail) {
                        alert("Ошибка: " + errorResponse.detail);
                    } else {
                        alert("Произошла ошибка при обработке запроса.");
                    }
                } catch (e) {
                    alert("Произошла неизвестная ошибка.");
                }
            }
        };

        zapros.send(JSON.stringify({ login: login, password: password }));
    }
}


function checkRegis(event) {
    var login = document.getElementById("login").value;
    var loginInput = document.getElementById("login");
    var password = document.getElementById("password").value;
    var passwordInput = document.getElementById("password");

    if (login.length < 1) {
        loginInput.classList.add('is-invalid');
        loginInput.classList.remove('is-valid');
    } else {
        loginInput.classList.remove('is-invalid');
        loginInput.classList.add('is-valid');
    }
    if (password.length < 8) {
        passwordInput.classList.add('is-invalid');
        passwordInput.classList.remove('is-valid');
    } else {
        passwordInput.classList.remove('is-invalid');
        passwordInput.classList.add('is-valid');
    }
    if (login.length > 1 && password.length >= 8) {
            var zapros = new XMLHttpRequest();
            zapros.open("POST", "/registration", true);
            zapros.setRequestHeader("Content-Type", "application/json");

            zapros.onload = function () {
                if (zapros.status === 200) {
                    window.location.href = "/";
                } else {
                    
                    try {
                        var errorResponse = JSON.parse(zapros.responseText);
                        if (errorResponse.error) {
                            alert("Ошибка: " + errorResponse.error);
                        } else {
                            alert("Произошла ошибка при обработке запроса.");
                        }
                    } catch (e) {
                        alert("Произошла неизвестная ошибка.");
                    }
                }
            };
            zapros.send(JSON.stringify({
                login: login,
                password: password
            }));
        }
    }


 



document.addEventListener('DOMContentLoaded', function () {
   
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
             
            const loginButton = document.querySelector('.b_c');
            
 
            if (loginButton) {
                loginButton.click();  
            }
            
        }
    });
});



document.addEventListener('DOMContentLoaded', function () {
    
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
           
 
            
            const b_r = document.querySelector('.b_r');
 
            if (b_r) {
                b_r.click();  
            }
        }
    });
});