// 파라미터 obj 객체 삭제 
function remove_btn(obj) {
    obj.parentNode.removeChild(obj);
}

// 로그인 안하고 대여시 로그인 해주세요 alert창
function login_alert() {
    alert("로그인을 해주세요");
}

// 도서 대여 ajax
function borrow_book(book_number, obj) {
    var httpRequest = new XMLHttpRequest();

    var result = confirm("대여하시겠습니까?");
    if (result){
        httpRequest.onreadystatechange = alertContents;
        httpRequest.open('GET', '/book_borrow?book_number='+book_number);
        httpRequest.send();

        function alertContents() {
            if (httpRequest.readyState === XMLHttpRequest.DONE) {
                if (httpRequest.status === 200) {
                    var book_div = document.getElementById('book_'+book_number);
                    remove_btn(obj);
            
                    var button = document.createElement("button");
                    button.setAttribute("id", 'book_return_'+book_number);
                    button.addEventListener("click", function() {
                        return_book(book_number, this);
                    });
                    button.innerHTML = "반납";
            
                    book_div.appendChild(button);

                    alert(httpRequest.responseText);
                } else {
                    alert('통신에 이상이 발생했습니다.');
                }
            }
        }
    }else {
        alert("대여가 취소되었습니다.");
    }
}


// 도서 반납 ajax
function return_book(book_number, obj) {
    var httpRequest = new XMLHttpRequest();

    var result = confirm("반납하시겠습니까?");
    if (result){
        httpRequest.onreadystatechange = alertContents;
        httpRequest.open('GET', '/book_return?book_number='+book_number);
        httpRequest.send();

        function alertContents() {
            if (httpRequest.readyState === XMLHttpRequest.DONE) {
                if (httpRequest.status === 200) {
                    var book_div = document.getElementById('book_'+book_number);
                    remove_btn(obj);

                    var button = document.createElement("button");
                    button.setAttribute("id", 'borrow_book_'+book_number);
                    button.addEventListener("click", function() {
                        borrow_book(book_number, this);
                    });
                    button.innerHTML = "대여";

                    book_div.appendChild(button);

                    alert(httpRequest.responseText);
                } else {
                    alert('통신에 이상이 발생했습니다.');
                }
            }
        }
    }else {
        alert("반납이 취소되었습니다.");
    }
}

function book_datails(obj, number) {
    document.getElementById('modal_detail').style.display='block';
    document.getElementsByClassName('book_image')[0].src = obj.getAttribute('src');
    document.getElementsByClassName('book_text')[0].innerHTML = document.getElementById('book_text_'+number).innerHTML;
    document.getElementsByClassName('book_name')[0].innerHTML = document.getElementById('book_name_'+number).innerHTML;
}
