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

            if (e.key === 'Backspace') {
                codeInputs.forEach((input, index2) => {
                    if (index1 <= index2 && prevInput) {
                        input.setAttribute('disabled', true);
                        currentInput.value = '';
                        prevInput.focus();
                    }
                });
            }

            if (!codeInputs[5].disabled && codeInputs[5].value !== '') {
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
    const allMenuItems = document.querySelector('#sidebar .side-menu .upper-menu');

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
    const tabs = document.querySelector('main .task-title'),
        allContent = document.querySelectorAll('main .important-tasks');

    if (tabs) {
        tabs.querySelectorAll('.title').forEach((button, index) => {
            button.addEventListener('click', function () {
                // e.preventDefault();

                if (!this.classList.contains('active')) {
                    tabs.querySelectorAll('.title').forEach(btn => {
                        btn.classList.remove('active');
                    });
                }

                this.classList.add('active');
                allContent.forEach(content => content.classList.remove('active'));
                allContent[index].classList.add('active');
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
            const menuIcon = item.querySelector('.icon'),
                menuOption = item.querySelector('.task-settings-box');

            if (e.target !== menuIcon) {
                if (e.target !== menuOption) {
                    if (menuOption.classList.contains('show')) {
                        menuOption.classList.remove('show');
                    }
                }
            }
        })
    });


    const allTaskHeads = document.querySelectorAll('main .task .head');
    allTaskHeads.forEach(item => {
        const taskStatusBtn = item.querySelector('.task-status-btn');
        taskStatusBtn.addEventListener('click', function () {
            const taskId = item.closest('.task').dataset.taskId;
            const taskStatus = item.querySelector('.task-status');
            const isCompleted = taskStatus.classList.contains('done');
            axios.defaults.xsrfCookieName = 'csrftoken';
            axios.defaults.xsrfHeaderName = 'X-CSRFToken';
            axios.post(`/tasks/${taskId}/update-status/`, {is_completed: !isCompleted})
                .then(response => {
                    if (response.status === 200) {
                        taskStatus.classList.toggle('done');
                        taskStatus.classList.toggle('bxs-circle');
                        taskStatus.classList.toggle('bxs-check-circle');
                        const taskStatusChange = item.querySelector('.task-status-change');
                        if (taskStatusChange.textContent === 'Позначити, як виконане') {
                            taskStatusChange.textContent = 'Позначити, як невиконане';
                        } else {
                            taskStatusChange.textContent = 'Позначити, як виконане';
                        }
                    } else {
                        throw new Error('Помилка оновлення статусу завдання.');
                    }
                })
                .catch(error => console.error(error));
        });
    });

    //
    //
    // const allTaskHeads = document.querySelectorAll('main .task .head');
    // allTaskHeads.forEach(item => {
    //     const taskStatus = item.querySelector('.task-status'),
    //         taskStatusBtn = item.querySelector('.task-status-btn'),
    //         taskStatusChange = item.querySelector('.task-status-change');
    //
    //
    //     taskStatusBtn.addEventListener('click', function () {
    //         const taskId = item.closest('.task').dataset.taskId;
    //         console.log("taskId", taskId);
    //         const isCompleted = taskStatus.classList.contains('done');
    //         const requestOptions = {
    //             method: 'POST',
    //             headers: {
    //                 'Content-Type': 'application/json',
    //                 'X-CSRFToken': '{{ csrf_token }}'
    //             },
    //             body: JSON.stringify({
    //                 is_completed: !isCompleted
    //             })
    //         };
    //
    //         fetch(`/tasks/${taskId}/update-status/`, requestOptions)
    //             .then(response => {
    //                 if (!response.ok) {
    //                     throw new Error('Помилка оновлення статусу завдання.');
    //                 }
    //                 return response.json();
    //             })
    //             .then(data => {
    //                 taskStatus.classList.toggle('done');
    //                 taskStatus.classList.toggle('bxs-circle');
    //                 taskStatus.classList.toggle('bxs-check-circle');
    //                 if (taskStatusChange.textContent === 'Позначити, як виконане') {
    //                     taskStatusChange.textContent = 'Позначити, як невиконане';
    //                 } else {
    //                     taskStatusChange.textContent = 'Позначити, як виконане';
    //                 }
    //             })
    //             .catch(error => console.error(error));
    //     });
    // });


    // const allTaskHeads = document.querySelectorAll('main .task .head');
    // allTaskHeads.forEach(item => {
    //     const taskStatus = item.querySelector('.task-status'),
    //         taskStatusBtn = item.querySelector('.task-status-btn'),
    //         taskStatusChange = item.querySelector('.task-status-change');
    //
    //     taskStatusBtn.addEventListener('click', function () {
    //         taskStatus.classList.toggle('done');
    //         taskStatus.classList.toggle('bxs-circle');
    //         taskStatus.classList.toggle('bxs-check-circle');
    //
    //         if (taskStatusChange.textContent === 'Позначити, як виконане') {
    //             taskStatusChange.textContent = 'Позначити, як невиконане';
    //         } else {
    //             taskStatusChange.textContent = 'Позначити, як виконане';
    //         }
    //     })
    // })
});

// // POP UP
// document.addEventListener('DOMContentLoaded', function () {
//     const section = document.querySelector('.tasks-class'),
//         overlay = document.querySelector('.overlay'),
//         createTaskBtn = document.querySelector('.create-task-btn'),
//         editTaskBtn = document.querySelectorAll('.edit-task-btn'),
//         closePopupBtn = document.querySelector('.close-icon');
//
//     function disableBodyScroll() {
//         document.documentElement.style.overflowY = 'hidden';
//         document.body.style.overflowY = 'hidden';
//     }
//
//     function enableBodyScroll() {
//         document.documentElement.style.overflowY = '';
//         document.body.style.overflowY = '';
//     }
//
//     createTaskBtn.addEventListener('click', () => {
//         section.classList.add('active');
//         disableBodyScroll();
//     });
//
//     editTaskBtn.forEach(btn => {
//         btn.addEventListener('click', () => {
//             section.classList.toggle('active');
//             disableBodyScroll();
//         });
//     });
//
//     closePopupBtn.addEventListener('click', () => {
//         section.classList.remove('active');
//         enableBodyScroll();
//     });
//
//     overlay.addEventListener('click', () => {
//         section.classList.remove('active');
//         enableBodyScroll();
//     });
// });


// CREATE TASK TAGS
document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-tag-input');
    const minusButton = document.getElementById('minus-tag-input');
    const tagInputs = document.getElementById('tag-inputs');
    let tagCount = 1;

    addButton.addEventListener('click', function () {
        tagCount++;
        const newTagInput = document.createElement('input');
        newTagInput.type = 'text';
        newTagInput.name = 'tags';
        newTagInput.placeholder = `Введіть тег`;
        tagInputs.appendChild(newTagInput);

        const minusIcon = document.createElement('i');
        minusIcon.classList.add('bx', 'bx-minus-circle', 'icon', 'remove-tag');
        const minusButton = document.createElement('div');
        minusButton.classList.add('add', 'minus-tag-input');
        minusButton.appendChild(minusIcon);
        tagInputs.appendChild(minusButton);

        minusButton.addEventListener('click', function () {
            tagInputs.removeChild(newTagInput);
            tagInputs.removeChild(minusButton);
            tagCount--;
        });
    });
});


// DELETE TASK
document.addEventListener('DOMContentLoaded', function () {
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
    const deleteLinks = document.querySelectorAll('.delete-link');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const confirmation = confirm('Ви впевнені, що хочете видалити це завдання?');
            if (confirmation) {
                const taskId = this.dataset.id;
                axios.delete(`/tasks/${taskId}/delete/`)
                    .then(response => {
                        console.log(response);
                        if (response.status === 204) {
                            const listItem = this.parentElement;
                            listItem.remove();
                            alert('Завдання успішно видалено');
                            location.reload();
                        }
                    })
                    .catch(error => {
                        console.error('Помилка під час виконання запиту:', error);
                        if (error.response.status === 403) {
                            alert('Ви не маєте дозволу на видалення цього завдання');
                        } else {
                            alert('Помилка під час видалення завдання');
                        }
                    });
            }
        });
    });
});

// FILE NAME SHOW
function displayFileName(inputId, spanId) {
    var fileInput = document.getElementById(inputId);
    var fileName = document.getElementById(spanId);

    if (fileInput.files.length > 0) {
        fileName.textContent = fileInput.files[0].name;
    } else {
        fileName.textContent = "";
    }
}

// ADD NEW FILES
document.addEventListener('DOMContentLoaded', function () {
    var counter = 0;

    // Функція для додавання нового поля для завантаження файлу
    function addFileInput() {
        var container = document.getElementById('file-inputs');
        var newInput = document.createElement('div');
        var inputId = 'file-upload-' + counter;
        var spanId = 'file-name-' + counter;
        newInput.innerHTML = '<br><br><label for="' + inputId + '" class="custom-file-upload">Завантажити</label> \
                              <input id="' + inputId + '" type="file" name="files" onchange="displayFileName(\'' + inputId + '\', \'' + spanId + '\')"/> \
                              <span id="' + spanId + '"></span><br><br>';
        container.appendChild(newInput);
        counter++;

        // Додавання кнопки для видалення поля для завантаження файлу
        var minusIcon = document.createElement('i');
        minusIcon.classList.add('bx', 'bx-minus-circle', 'icon', 'remove-file');
        var minusButton = document.createElement('div');
        minusButton.classList.add('add', 'minus-file-input');
        minusButton.appendChild(minusIcon);
        container.appendChild(minusButton);

        minusButton.addEventListener('click', function () {
            container.removeChild(newInput); // Видалення поля для завантаження файлу
            container.removeChild(minusButton); // Видалення кнопки мінус
            counter--;
        });
    }

    document.getElementById('add-file-input').addEventListener('click', addFileInput);
});
