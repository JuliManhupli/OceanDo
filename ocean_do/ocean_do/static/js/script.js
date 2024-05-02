// CODE VERIFICATION
document.addEventListener('DOMContentLoaded', function () {
    const codeInputs = document.querySelectorAll('.code-input');
    const verifyCodeBtn = document.querySelector('.code-verify-btn');

    if (codeInputs && verifyCodeBtn) {
        codeInputs.forEach((input, index1) => {
            input.addEventListener('keyup', (e) => {
                const currentInput = input, nextInput = input.nextElementSibling, prevInput = input.previousElementSibling;

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
    }

});

/* SIDEBAR */
// MENU
document.addEventListener('DOMContentLoaded', function () {
    const allMenuItems = document.querySelector('#sidebar .side-menu .upper-menu li:not(:last-child)');

    if (allMenuItems) {
        allMenuItems.querySelectorAll('a').forEach(a => {
            a.addEventListener('click', function () {

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

// DROPDOWN
document.addEventListener('DOMContentLoaded', function () {
    const allDropdown = document.querySelectorAll('#sidebar .side-dropdown'),
        upperPartMenu = document.querySelector('.upper-menu');

    allDropdown.forEach(item => {
        const a = item.parentElement.querySelector('a:first-child');
        a.addEventListener('click', function () {
            if (!this.classList.contains('active')) {
                allDropdown.forEach(i => {
                    const aLink = i.parentElement.querySelector('a:first-child');

                    aLink.classList.remove('active');
                    i.classList.remove('show');
                })
                upperPartMenu.style.marginBottom = '200px';
            } else {
                upperPartMenu.style.marginBottom = '';
            }
            this.classList.toggle('active');
            item.classList.toggle('show');
        })
    })
});

document.addEventListener('DOMContentLoaded', function () {
    const toggleSidebar = document.querySelector('nav .toggle-sidebar');
    const sidebar = document.getElementById('sidebar');

    toggleSidebar.addEventListener('click', function () {
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
    // OLD
    // const allTaskItems = document.querySelectorAll('.task-settings');
    // console.log(allTaskItems);
    // allTaskItems.forEach(item => {
    //     const menuIcon = item.querySelector('.icon');
    //     const menuOption = item.querySelector('.task-settings-box');
    //
    //     menuIcon.addEventListener('click', function () {
    //         menuOption.classList.toggle('show');
    //     })
    // })

    const tasksContainers = document.querySelectorAll('.important-tasks');
    tasksContainers.forEach(tasksContainer => {
        tasksContainer.addEventListener('click', function(event) {
            console.log('Clicked!', event.target);
            if (event.target.closest('.task-settings .icon')) {
                const menuOption = event.target.closest('.task-settings').querySelector('.task-settings-box');
                if (menuOption) {
                    menuOption.classList.toggle('show');
                }
            }
        });
    });

    // OLD
    // window.addEventListener('click', function (e) {
    //     allTaskItems.forEach(item => {
    //         const menuIcon = item.querySelector('.icon'),
    //             menuOption = item.querySelector('.task-settings-box');
    //
    //         if (e.target !== menuIcon) {
    //             if (e.target !== menuOption) {
    //                 if (menuOption.classList.contains('show')) {
    //                     menuOption.classList.remove('show');
    //                 }
    //             }
    //         }
    //     })
    // });

    document.addEventListener('click', function (e) {
        tasksContainers.forEach(tasksContainer => {
            const menuOptions = tasksContainer.querySelectorAll('.task-settings-box');
            menuOptions.forEach(menuOption => {
                const isIconClicked = e.target.closest('.task-settings .icon');
                const isMenuClicked = e.target.closest('.task-settings-box');

                if (!isIconClicked && !isMenuClicked && menuOption.classList.contains('show')) {
                    menuOption.classList.remove('show');
                }
            })
        });
    });


    document.addEventListener('click', function (e) {
        tasksContainers.forEach(tasksContainer => {
            axios.defaults.xsrfCookieName = 'csrftoken';
            axios.defaults.xsrfHeaderName = 'X-CSRFToken';
            const deleteLinks = tasksContainer.querySelectorAll('.delete-link');

            deleteLinks.forEach(link => {
                link.removeEventListener('click', onDeleteClick);
            });

            deleteLinks.forEach(link => {
                link.addEventListener('click', onDeleteClick);
            });
        });
    });
    // const allTaskHeads = document.querySelectorAll('.task-settings');
    // allTaskHeads.forEach(item => {
    //     const taskStatusBtn = item.querySelector('.task-status-btn');
    //     if (taskStatusBtn) {
    //         taskStatusBtn.addEventListener('click', function () {
    //             const taskId = item.closest('.task').dataset.taskId;
    //             const taskStatus = item.querySelector('.task-status');
    //             console.log(taskStatus);
    //             const isCompleted = taskStatus.classList.contains('done');
    //             axios.defaults.xsrfCookieName = 'csrftoken';
    //             axios.defaults.xsrfHeaderName = 'X-CSRFToken';
    //             axios.post(`/tasks/${taskId}/update-status/`, {is_completed: !isCompleted})
    //                 .then(response => {
    //                     if (response.status === 200) {
    //                         taskStatus.classList.toggle('done');
    //                         taskStatus.classList.toggle('bxs-circle');
    //                         taskStatus.classList.toggle('bxs-check-circle');
    //                         const taskStatusChange = item.querySelector('.task-status-change');
    //                         if (taskStatusChange.textContent === 'Позначити, як виконане') {
    //                             taskStatusChange.textContent = 'Позначити, як невиконане';
    //                         } else {
    //                             taskStatusChange.textContent = 'Позначити, як виконане';
    //                         }
    //                     } else {
    //                         throw new Error('Помилка оновлення статусу завдання.');
    //                     }
    //                 })
    //                 .catch(error => console.error(error));
    //         });
    //     }
    // });
});


// DELETE TASK FROM CREATOR INFO
document.addEventListener('DOMContentLoaded', function () {
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
    const deleteLinks = document.querySelectorAll('.delete-link');
    console.log("deleteLinks");
    console.log(deleteLinks);
    deleteLinks.forEach(link => {
        link.removeEventListener('click', onDeleteClick);
    });

    deleteLinks.forEach(link => {
        link.addEventListener('click', onDeleteClick);
    });
});

function onDeleteClick(event) {
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
}

// CREATE TASK TAGS
document.addEventListener('DOMContentLoaded', function () {
    const addButton = document.getElementById('add-tag-input');
    const tagInputs = document.getElementById('tag-inputs');
    let tagCount = 1;
    if (addButton && tagInputs) {
        addButton.addEventListener('click', function () {
            tagCount++;

            const tagWrapper = document.createElement('div');
            tagWrapper.classList.add('tag-wrapper');

            const newTagInput = document.createElement('input');
            newTagInput.type = 'text';
            newTagInput.name = 'tags';
            newTagInput.placeholder = "Введіть тег";

            const minusIcon = document.createElement('i');
            minusIcon.classList.add('bx', 'bx-minus-circle', 'icon', 'remove-tag');

            const minusButton = document.createElement('div');
            minusButton.classList.add('add', 'minus-tag-input');

            tagWrapper.appendChild(newTagInput);
            minusButton.appendChild(minusIcon);
            tagWrapper.appendChild(minusButton);
            tagInputs.appendChild(tagWrapper);

            minusButton.addEventListener('click', function () {
                tagInputs.removeChild(tagWrapper);
                tagCount--;
            });
        });
    }
});

// CREATE TASK FOLDERS
document.addEventListener('DOMContentLoaded', function () {
    const addButton = document.getElementById('add-folder-input');
    const folderInputs = document.getElementById('folder-inputs');
    let folderCount = 0;
    if (addButton && folderInputs) {
        addButton.addEventListener('click', function () {
            folderCount++;

            const folderWrapper = document.createElement('div');
            folderWrapper.classList.add('folder-wrapper');

            const newFolderInput = document.createElement('input');
            newFolderInput.type = 'text';
            newFolderInput.placeholder = "Введіть назву папки";
            newFolderInput.name = "folders";

            const minusIcon = document.createElement('i');
            minusIcon.classList.add('bx', 'bx-minus-circle', 'icon', 'remove-folder');

            const minusButton = document.createElement('div');
            minusButton.classList.add('add', 'minus-folder-input');

            folderWrapper.appendChild(newFolderInput);
            minusButton.appendChild(minusIcon);
            folderWrapper.appendChild(minusButton);
            folderInputs.appendChild(folderWrapper);

            minusButton.addEventListener('click', function () {
                folderInputs.removeChild(folderWrapper);
                folderCount--;
            });
        });
    }
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
        var fileWrapper = document.createElement('div');
        fileWrapper.classList.add('file-wrapper');

        var container = document.getElementById('file-inputs');
        var newInput = document.createElement('div');
        var inputId = 'file-upload-' + counter;
        var spanId = 'file-name-' + counter;

        newInput.innerHTML = '<label for="' + inputId + '" class="custom-file-upload">Завантажити</label> \
                              <input id="' + inputId + '" type="file" name="files" onchange="displayFileName(\'' + inputId + '\', \'' + spanId + '\')"/> \
                              <span id="' + spanId + '"></span>';

        // Додавання кнопки для видалення поля для завантаження файлу
        var minusIcon = document.createElement('i');
        minusIcon.classList.add('bx', 'bx-minus-circle', 'icon', 'remove-file');
        var minusButton = document.createElement('div');
        minusButton.classList.add('add', 'minus-file-input');

        fileWrapper.appendChild(newInput);
        minusButton.appendChild(minusIcon);
        fileWrapper.appendChild(minusButton);
        container.appendChild(fileWrapper);
        counter++;

        minusButton.addEventListener('click', function () {
            container.removeChild(fileWrapper);
            counter--;
        });
    }

    const addFileInputBtn = document.getElementById('add-file-input');
    if (addFileInputBtn) {
        addFileInputBtn.addEventListener('click', addFileInput);
    }
});


// DELETE AVATAR
function deleteAvatar() {
    const confirmation = confirm('Ви впевнені, що хочете видалити фото профілю?');
    if (confirmation) {
        axios.delete("/users/delete-avatar/")
            .then(response => {
                console.log(response);
                if (response.status === 204) {
                    window.location.reload();
                    alert("Фото профілю було успішно видалено.");

                }
            })
            .catch(error => {
                console.error("Помилка при видаленні фото профілю:", error);
                alert("Сталася помилка під час видалення фото профілю. Будь ласка, спробуйте ще раз.");
            });
    }
}

// NOTIFICATIONS
const notificationSocket = new WebSocket("ws://" + window.location.host + "/ws/notifications/");

notificationSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data);
    console.log("data" + data);
    document.getElementById('notification-dropdown').innerHTML = `<li>${data.message}</li>` + document.getElementById('notification-dropdown').innerHTML;

    // Update notification count in local storage
    let numberOfNotifications = parseInt(localStorage.getItem('notificationCount')) || 0;
    localStorage.setItem('notificationCount', numberOfNotifications + 1);
    updateNotificationCount();

    console.log("numberOfNotifications: " + numberOfNotifications);
};

notificationSocket.onclose = function () {
    console.error('Chat socket closed unexpectedly');
};

// Function to clear notification count from local storage
function clearNotificationCount() {
    localStorage.removeItem('notificationCount');
    updateNotificationCount(); // Update the displayed count
}

// Function to update the notification count
function updateNotificationCount() {
    let numberSpan = document.getElementById('notification-number');
    let numberOfNotifications = parseInt(localStorage.getItem('notificationCount')) || 0;
    if (numberOfNotifications === 0) {
        numberSpan.style.display = 'none';
    } else {
        numberSpan.style.display = 'flex';
        numberSpan.innerHTML = numberOfNotifications;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    updateNotificationCount();

    const notifBlock = document.querySelectorAll('.notification-block');
    notifBlock.forEach(item => {
        const bellIcon = item.querySelector('.icon');
        const allNotifs = item.querySelector('.dropdown-menu');

        bellIcon.addEventListener('click', function () {
            allNotifs.classList.toggle('show');

            // Clear notification count when bell icon is clicked
            localStorage.setItem('notificationCount', 0);
            // updateNotificationCount();
            clearNotificationCount();
        })
    })

    window.addEventListener('click', function (e) {
        notifBlock.forEach(item => {
            const bellIcon = item.querySelector('.icon');
            const allNotifs = item.querySelector('.dropdown-menu');

            if (!bellIcon.contains(e.target) && !allNotifs.contains(e.target)) {
                if (allNotifs.classList.contains('show')) {
                    allNotifs.classList.remove('show');
                }
            }
        })
    });

    document.getElementById('logout-btn').addEventListener('click', function () {
        clearNotificationCount();
    });
});

// USERS IN TASK INFO
document.addEventListener('DOMContentLoaded', function () {
    const allUsers = document.querySelector('main .creator-user-view .left-users .users-ul');

    if (allUsers) {
        allUsers.querySelectorAll('a').forEach(a => {
            a.addEventListener('click', function () {

                if (!this.classList.contains('active')) {
                    allUsers.querySelectorAll('a').forEach(i => {
                        i.classList.remove('active');
                    })
                }

                this.classList.add('active');
            });
        });
    }
});


// USERS TAB
document.addEventListener('DOMContentLoaded', function () {
    const tabsUsers = document.querySelector('main .creator-user-view .left-users .users-ul'),
        allUsersInfo = document.querySelectorAll('main .creator-user-view .users-data-block .user-info');

    if (tabsUsers) {
        tabsUsers.querySelectorAll('li').forEach((a, index) => {
            a.addEventListener('click', function () {

                if (!this.classList.contains('active')) {
                    tabsUsers.querySelectorAll('li').forEach(link => {
                        link.classList.remove('active');
                    });
                }

                this.classList.add('active');
                allUsersInfo.forEach(info => info.classList.remove('active'));
                allUsersInfo[index].classList.add('active');
            });
        });
    }
});


// FUNCTIONS FOR CHECKING DATE
function translateMonth(month) {
        const months = {
            'січня': 'January',
            'лютого': 'February',
            'березня': 'March',
            'квітня': 'April',
            'травня': 'May',
            'червня': 'June',
            'липня': 'July',
            'серпня': 'August',
            'вересня': 'September',
            'жовтня': 'October',
            'листопада': 'November',
            'грудня': 'December'
        };
        return months[month];
    }
function parseUkrainianDate(dateString) {
        const [day, monthInUkrainian, year] = dateString.split(' ');
        const translatedMonth = translateMonth(monthInUkrainian);
        return new Date(`${translatedMonth} ${day}, ${year}`);
}

// USER TASK STATUS CHANGE
document.addEventListener('DOMContentLoaded', function () {
    const completeTaskBtn = document.getElementById('update-status-btn'),
        userTaskStatus = document.querySelector('.user-task-status'),
        completeTaskFormBtn = document.querySelector('.task-done-form .complete-task'),
        sendTaskFilesBtn = document.getElementById('send-task-files'),
        addTaskFilesBtn = document.getElementById('add-file-input'),
        fileInputsContainer = document.getElementById('file-inputs'),
        allDeleteFileBtns = document.querySelectorAll('.files-container .file-div .user-file-btns .delete-file-btn');

    const userDeadline = parseUkrainianDate(taskUserDeadline),
    userTime = new Date(userDeadline.getFullYear(), userDeadline.getMonth(), userDeadline.getDate());

    const todayDate = new Date(),
    todayTime = new Date(todayDate.getFullYear(), todayDate.getMonth(), todayDate.getDate());
    console.log("YES")
    console.log(userTime);
    console.log(todayTime);
    const isOverdue = userTime < todayTime;
    console.log(isOverdue);
    if (isOverdue){
        completeTaskBtn.classList.toggle('overdue');
    }

    // Function to update task status color
    function updateTaskStatusColor(isCompleted, overDue) {
        if (isCompleted) {
            userTaskStatus.style.background = 'var(--green)';
            userTaskStatus.style.color = 'white';

            addTaskFilesBtn.style.opacity = '0.5';
            addTaskFilesBtn.style.pointerEvents = 'none';
            sendTaskFilesBtn.style.opacity = '0.5';
            sendTaskFilesBtn.style.pointerEvents = 'none';
            allDeleteFileBtns.forEach(button => {
                button.style.opacity = '0.5';
                button.style.pointerEvents = 'none';
            });
        } else {
            if (overDue) {
                userTaskStatus.style.background = 'var(--red)';
                userTaskStatus.style.color = 'white';
            } else {
                userTaskStatus.style.background = 'var(--yellow)';
                userTaskStatus.style.color = 'black';
            }

            addTaskFilesBtn.style.opacity = '1';
            addTaskFilesBtn.style.pointerEvents = 'auto';
            sendTaskFilesBtn.style.opacity = '1';
            sendTaskFilesBtn.style.pointerEvents = 'auto';
            allDeleteFileBtns.forEach(button => {
                button.style.opacity = '1';
                button.style.pointerEvents = 'auto';
            });
        }
    }

    if (completeTaskBtn && userTaskStatus && completeTaskFormBtn) {
        completeTaskFormBtn.addEventListener('click', function () {

            // Check if file inputs are present and not empty
            const fileInputs = document.querySelector('#file-inputs .file-wrapper div span');

            if (fileInputsContainer.children.length !== 0 &&
                fileInputs.textContent.trim() !== ''){
                updateTaskStatus();
            } else {
                alert('Додайте файл перед відправленням або відправте без файлів за допомогою кнопки нижче!');
            }
        });

        completeTaskBtn.addEventListener('click', updateTaskStatus);

        function updateTaskStatus(){

            const confirmed = confirm('Ви впевнені, що хочете відправити завдання?');
            if (!confirmed) {
                return;
            }
            const taskId = document.getElementById('task-info').dataset.taskId;
            const isCompleted = !completeTaskBtn.classList.contains('completed');
            axios.defaults.xsrfCookieName = 'csrftoken';
            axios.defaults.xsrfHeaderName = 'X-CSRFToken';
            axios.post(`/tasks/${taskId}/update-status/`, {is_completed: isCompleted})
                .then(response => {
                    if (response.status === 200) {
                        completeTaskBtn.textContent = isCompleted ? 'Позначити як невиконане' : 'Позначити як виконане';
                        completeTaskBtn.classList.toggle('completed');
                        userTaskStatus.textContent = isCompleted ? 'Виконано' : 'У процесі виконання';
                        updateTaskStatusColor(isCompleted, isOverdue);

                    } else {
                        // Оновлення статусу не вдалося
                        console.error('Помилка оновлення статусу завдання.');
                    }
                })
                .catch(error => console.error(error));
        }

        if (completeTaskBtn.classList.contains('completed')) {
            updateTaskStatusColor(true, false);
        } else if (completeTaskBtn.classList.contains('overdue')){
            updateTaskStatusColor(false, true);
        }
    }
});

// DELETE FILE FROM USERS SENT TASK
document.addEventListener('DOMContentLoaded', function () {
    const deleteFileButtons = document.querySelectorAll('.delete-file-btn');
    if (deleteFileButtons) {
        deleteFileButtons.forEach(button => {
            button.addEventListener('click', function () {
                const fileId = button.dataset.fileId;
                const confirmation = confirm('Ви впевнені, що хочете видалити цей файл?');
                if (confirmation) {
                    axios.defaults.xsrfCookieName = 'csrftoken';
                    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
                    axios.post(`/tasks/files/delete/${fileId}/`)
                        .then(response => {
                            if (response.status === 200) {
                                // Remove the file from the UI
                                button.parentElement.parentElement.remove();

                                // Check if container div is empty
                                const container = document.querySelector('.files-container');
                                if (!container.querySelector('.file-div')) {
                                    container.remove();
                                }
                            } else {
                                console.error('Failed to delete file.');
                            }
                        })
                        .catch(error => console.error(error));
                }
            });
        });
    }
});

// CREATOR VIEW TASK STATUS OF USERS AND THE TASK
document.addEventListener("DOMContentLoaded", function() {
    const taskStatuses = document.querySelectorAll(".check-status");

    const taskDeadline = parseUkrainianDate(deadLineTime),
    taskTime = new Date(taskDeadline.getFullYear(), taskDeadline.getMonth(), taskDeadline.getDate());
    const today = new Date(),
    todayTime = new Date(today.getFullYear(), today.getMonth(), today.getDate());

    if (taskStatuses) {
        taskStatuses.forEach(taskStatus => {
            const isCompleted = taskStatus.textContent.trim() === "Виконано";
            const isOverdue = taskTime < todayTime;

            if (isCompleted) {
                taskStatus.style.backgroundColor = "var(--green)";
                taskStatus.style.color = "white";
            } else if (isOverdue) {
                taskStatus.style.backgroundColor = "var(--red)";
                taskStatus.style.color = "white";
            } else {
                taskStatus.style.backgroundColor = "var(--yellow)";
                taskStatus.style.color = "black";
            }
        });
    }
});


// SIDE MENU FOLDERS
document.addEventListener('DOMContentLoaded', function () {
    const sideDropdown = document.getElementById('side-menu-folders');
    const folderMenu = document.querySelector('.folder-menu');

    if (sideDropdown) {
        fetch('/tasks/get-side-menu-folder/')
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    data.forEach(folder => {
                        const listItem = document.createElement('li');
                        listItem.innerHTML = `<a href="/tasks/folders/${folder.id}/">${folder.name}</a>`;
                        sideDropdown.appendChild(listItem);
                    });
                    // Показати меню папок
                    folderMenu.style.display = 'block';
                }
            })
            .catch(error => console.error('Error fetching user folders:', error));
    }
});


// CALERNDAR
document.addEventListener('DOMContentLoaded', function () {
    const date = document.querySelector('.date'),
        daysContainer = document.querySelector('.days'),
        prev = document.querySelector('.prev'),
        next = document.querySelector('.next'),
        todayBtn = document.querySelector('.today-btn'),
        tasksContainer = document.querySelector('.calendar-tasks');

    let today = new Date();
    let activeDay;
    let month = today.getMonth();
    let year = today.getFullYear();

    const months = [
        "Січень",
        "Лютий",
        "Березень",
        "Квітень",
        "Травень",
        "Червень",
        "Липень",
        "Серпень",
        "Вересень",
        "Жовтень",
        "Листопад",
        "Грудень",
    ];

    // add days
    function initCalendar() {

        const firstDay = new Date(year, month, 1),
            lastDay = new Date(year, month + 1, 0),
            prevLastDay = new Date(year, month, 0),
            prevDays = prevLastDay.getDate(),
            lastDate = lastDay.getDate(),
            day = (firstDay.getDay() + 6) % 7,
            nextDays = (7 - lastDay.getDay()) % 7;

        // update calendar head
        date.innerHTML = months[month] + " " + year;

        //add days to squares
        let days = "";

        //previous month days
        for (let x = day; x > 0; x--) {
            days += `<div class="day prev-date">${prevDays - x + 1}</div>`;
        }

        // current month days
        for (let i = 1; i <= lastDate; i++) {

            //if task ends on this day
            let task = false;
            tasksJson.forEach((taskObj) => {
                if (
                    taskObj.day === i &&
                    taskObj.month === month + 1 &&
                    taskObj.year === year
                ) {
                    task = true;
                }
            });


            //if it is today then add class 'today'
            if (
                i === new Date().getDate() &&
                month === new Date().getMonth() &&
                year === new Date().getFullYear()
            ) {

                //if task is on this day - add task class
                if (task) {
                    days += `<div class="day today task-present">${i}</div>`; //active
                } else {
                    days += `<div class="day today">${i}</div>`; //active
                }
            } else {
                // updateTasks(i);
                //add other days
                if (task) {
                    days += `<div class="day task-present">${i}</div>`;
                } else {
                    days += `<div class="day">${i}</div>`;
                }
            }
        }

        // next month
        for (let j = 1; j <= nextDays; j++) {
            days += `<div class="day next-date">${j}</div>`;
        }

        // calendar initialisation
        daysContainer.innerHTML = days;
        addListener();
    }

    initCalendar();

    function prevMonth() {
        month--;
        if (month < 0) {
            month = 11;
            year--;
        }
        initCalendar();
    }

    function nextMonth() {
        month++;
        if (month > 11) {
            month = 0;
            year++;
        }
        initCalendar();
    }

    // change monthes
    prev.addEventListener('click', prevMonth);
    next.addEventListener('click', nextMonth);

    // go to today
    todayBtn.addEventListener('click', () => {
        today = new Date();
        month = today.getMonth();
        year = today.getFullYear();
        initCalendar();
    });


    // function that adds listener on days with tasks deadlines
    function addListener() {
        const days = document.querySelectorAll('.day');
        days.forEach((day) => {
            day.addEventListener('click', (e) => {
                //set current day as an active one
                activeDay = Number(e.target.innerHTML);

                //remove other 'active' day
                days.forEach((day) => {
                    day.classList.remove('active');
                });

                // go to prev month if prev month day is clicked
                if (e.target.classList.contains('prev-date')) {
                    prevMonth();

                    setTimeout(() => {
                        // select days of clicked month
                        const days = document.querySelectorAll('.day');

                        // then add class 'active' to clicked
                        days.forEach((day) => {
                            if (
                                !day.classList.contains('prev-date') &&
                                day.innerHTML === e.target.innerHTML
                            ) {
                                day.classList.add('active');
                                //added here
                                days.forEach((todayDay) => {
                                    if (day !== todayDay) {
                                        todayDay.classList.remove('active');
                                    }
                                });
                                updateTasks(activeDay);
                            }
                        });
                    }, 100);
                    // go to next month if next month day is clicked
                } else if (e.target.classList.contains('next-date')) {
                    nextMonth();

                    setTimeout(() => {
                        // select days of clicked month
                        const days = document.querySelectorAll('.day');

                        // then add class 'active' to clicked
                        days.forEach((day) => {
                            if (
                                !day.classList.contains('next-date') &&
                                day.innerHTML === e.target.innerHTML
                            ) {
                                day.classList.add('active');
                                //added here
                                days.forEach((todayDay) => {
                                    if (day !== todayDay) {
                                        todayDay.classList.remove('active');
                                    }
                                });
                                updateTasks(activeDay);
                            }
                        });
                    }, 100);
                } else {
                    // stay in the current month
                    e.target.classList.add('active');
                    //added here
                    days.forEach((todayDay) => {
                        if (day !== todayDay) {
                            todayDay.classList.remove('active');
                        }
                    });
                    updateTasks(activeDay);
                }
            });
        });
    }

    function updateTasks(date) {
        let tasks = "";
        const todayDate = new Date(),
        todayTime = new Date(todayDate.getFullYear(), todayDate.getMonth(), todayDate.getDate());
        tasksJson.forEach((task) => {
            //get tasks on active day
            if (
                date === task.day &&
                month + 1 === task.month &&
                year === task.year
            ) {
                // then show
                let foldersHTML = "";
                if (task.folders.length > 0) {
                    task.folders.forEach(folder => {
                        foldersHTML += `<p class="folder-name">${folder}</p><p class="folder-name">|</p>`;
                    });
                }

                let tagsHTML = '';
                if (task.tags.length > 0) {
                    task.tags.forEach(tag => {
                        tagsHTML += `<p>${tag}</p>`;
                    });
                }

                const deadLine = parseUkrainianDate(task.date),
                    deadLineTime = new Date(deadLine.getFullYear(), deadLine.getMonth(), deadLine.getDate());
                const isOverdue = deadLineTime < todayTime;

                tasks += `
                        <div class="task" data-task-id="${task.id}">
                            <div class="head">`

                if (task.category === 'Виконання') {
                        tasks += `<div onclick='location.href="/tasks/task-info/${task.id}";'>`
                } else {
                        tasks += `<div onclick='location.href="/tasks/task-info-creator/${task.id}";'>`
                }
                tasks += `
                                    <div class="status">
                                        <p class="category">${task.category}</p>
                                        `

                if (isOverdue){
                    tasks += `
                          <i class='bx bxs-x-circle icon task-status overdue'></i>
                          `
                } else {
                   tasks += `
                          <i class='bx bxs-circle icon task-status'></i>
                          `
                }

                tasks += `
                                    </div>
                                    <div class="folder">
                                        <i class='bx bx-folder icon'></i>
                                        ${foldersHTML}
                                    </div>
                                </div>
                                <div class="task-settings">
                                    <i class='bx bx-dots-horizontal-rounded icon'></i>
                                    <ul class="task-settings-box">`
                if (task.type === 'assigned') {
                        tasks += `
                        <a href="/tasks/${task.id}/assign-edit/" class="edit-task-btn">
                            <li>Змінити теги і папки</li>
                        </a>
                        `
                } else {
                        tasks += `
                        <a href="/tasks/${task.id}/edit/" class="edit-task-btn">
                             <li>Змінити</li>
                        </a>
                        <a href="#" class="delete-link" data-id="${task.id}">
                            <li>Видалити</li>
                        </a>
                        `
                }
                tasks += `           
                                      </ul>
                                </div>
                            </div>
                            `
                if (task.category === 'Виконання') {
                        tasks += `<div onclick='location.href="/tasks/task-info/${task.id}";'>`
                } else if (task.type === 'created') {
                        tasks += `<div onclick='location.href="/tasks/task-info-creator/${task.id}";'>`
                }

                tasks += `
                                <h2 class="name">${task.name}</h2>
                                <div class="tag-box">
                                    ${tagsHTML}
                                </div>
                                <div class="limit-block">
                                    <p class="limit-block-title">Термін виконання:</p>
                                    <p class="time-limit">${task.date}</p>
                                </div>
                                <div class="participants">
                                    <i class='bx bxs-user icon'></i>
                                    <p class="user-number">${task.users}</p>
                                </div>
                            </div>
                        </div>
                 `;
            }
        });

        //If no task on this day
        if (tasks === '') {
            tasks = `
            <div class="no-task">
                <h3>Завдань нема</h3>
            </div>
            `;
        }

        tasksContainer.innerHTML = tasks;
    }
});