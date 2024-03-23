// CODE VERIFICATION
document.addEventListener('DOMContentLoaded', function () {
    const codeInputs = document.querySelectorAll('.code-input');
    const verifyCodeBtn = document.querySelector('.code-verify-btn');

    codeInputs.forEach((input, index1) => {
        input.addEventListener('keyup', (e) => {
            const currentInput = input,
                nextInput = input.nextElementSibling,
                prevInput = input.previousElementSibling;

            // if user writes more than 1 number - clear out
            if (currentInput.value.length > 1) {
                currentInput.value = '';
                return;
            }

            if (nextInput && nextInput.hasAttribute('disabled') && currentInput.value !== '') {
                nextInput.removeAttribute('disabled');
                nextInput.focus();
            }

            if (e.key == 'Backspace') {
                codeInputs.forEach((input, index2) => {
                    if (index1 <= index2 && prevInput) {
                        input.setAttribute('disabled', true);
                        currentInput.value = '';
                        prevInput.focus();
                    }
                });
            }

            if (!codeInputs[3].disabled && codeInputs[3].value !== '') {
                verifyCodeBtn.classList.add('active');
                return;
            }
            verifyCodeBtn.classList.remove('active');
        });
    });

    codeInputs[0].focus();
});


/* SIDEBAR */
document.addEventListener('DOMContentLoaded', function () {
    const allMenuItems = document.querySelector('#sidebar .side-menu');

    if (allMenuItems) {
        allMenuItems.querySelectorAll('a').forEach(a => {
            a.addEventListener('click', function () {
                // e.preventDefault();

                if (!this.classList.contains('active')) {
                    allMenuItems.querySelectorAll('a').forEach(i => {
                        i.classList.remove('active');
                    })
                }

                this.classList.add('active');
            });
        });
    }
});


document.addEventListener('DOMContentLoaded', function() {
    const toggleSidebar = document.querySelector('nav .toggle-sidebar');
    const sidebar = document.getElementById('sidebar');

    toggleSidebar.addEventListener('click', function() {
        sidebar.classList.toggle('hide');
    });
});

// TASK TAB
document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelector('main .task-title');

    if (tabs) {
        tabs.querySelectorAll('.title').forEach(button => {
            button.addEventListener('click', function () {
                // e.preventDefault();

                if (!this.classList.contains('active')) {
                    tabs.querySelectorAll('.title').forEach(btn => {
                        btn.classList.remove('active');
                    });
                }

                this.classList.add('active');
            });
        });
    }
});

// TASK MENU
document.addEventListener('DOMContentLoaded', function () {
    const allTaskItems = document.querySelectorAll('main .task .head .task-settings');
    allTaskItems.forEach(item => {
        const menuIcon = item.querySelector('.icon');
        const menuOption = item.querySelector('.task-settings-box');

        menuIcon.addEventListener('click', function () {
            menuOption.classList.toggle('show');
        })
    })

    window.addEventListener('click', function (e) {
        allTaskItems.forEach(item => {
            const menuIcon = item.querySelector('.icon');
            const menuOption = item.querySelector('.task-settings-box');

            if (e.target !== menuIcon) {
                if (e.target !== menuOption) {
                    if (menuOption.classList.contains('show')) {
                        menuOption.classList.remove('show');
                    }
                }
            }
        })
    });
});

// POP UP
document.addEventListener('DOMContentLoaded', function() {

    const section = document.querySelector('.tasks-class'),
        overlay = document.querySelector('.overlay'),
        createTaskBtn = document.querySelector('.create-task-btn'),
        closePopupBtn = document.querySelector('.close-icon');

    createTaskBtn.addEventListener('click', function() {
        section.classList.add('active');
    });

    closePopupBtn.addEventListener('click', function() {
        section.classList.remove('active');
    });

    overlay.addEventListener('click', function() {
        section.classList.remove('active');
    });
});
