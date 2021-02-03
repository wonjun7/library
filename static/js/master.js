function button_event(){
  
    if (confirm("정말 삭제하시겠습니까??") == true){    //확인
        var form = document.check;
        form.submit();
    
    }else{   //취소
        return;
      }
    }

function book_insert() {
  document.getElementById('modal_book_insert').style.display='block';
}