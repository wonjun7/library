// 아이디 중복체크
function id_double_check() {
    var httpRequest = new XMLHttpRequest();

    var ck_id = document.getElementById('id').value;

    httpRequest.onreadystatechange = check_id;
    httpRequest.open('POST',"/check_id2");
    httpRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    httpRequest.send("id="+ck_id);

    function check_id() {
            if (httpRequest.readyState === XMLHttpRequest.DONE) {
                if (httpRequest.status === 200) {
                        alert(httpRequest.responseText);
                }else {
                alert('통신에 이상이 발생했습니다.');
            }
        }
    }
}