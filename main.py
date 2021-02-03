import sys, mariadb, os
from flask import Flask, render_template, request, session

app = Flask(__name__)

# Oracle Cloud MariaDB Connect
def get_conn():
    conn = mariadb.connect(
        user="root",
        password="password",
        host="193.122.100.83",
        port=13306,
        database="LIBRARY"
    )
    return conn

@app.route('/')
def opening():
    return render_template("/opening.html")

@app.route('/intro')
def intro():
    return render_template("/intro.html")

@app.route('/main')
def main():
    return render_template("/main.html")

#로그인 화면
@app.route('/sign_in')
def sign_in():
    if 'number' in session:
        r_num = session['number']
        alert = """
                <script>
                    alert("잘못된 접근입니다.")
                </script>
                """
        return render_template('/main.html', alert=alert)
    return render_template("/sign_in.html")

#로그인 화면에서 입력한 ID와 PW 체크 (DB에 있는지 여부 확인)
@app.route('/sign_in', methods=['POST'])
def check_id():
    insert_id = request.form['id']
    insert_pw = request.form['pw']
    login_flag = False

    result =""

    sql = "SELECT ID, PW, NUMBER FROM MEMBER WHERE ID = '{}'".format(insert_id)
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        for (ID, PW, NUMBER) in cur:
            result = "{0},{1}".format(ID,PW)

            # 입력한 ID와 PW가 DB와 일치하는 경우
            if ID == insert_id and PW == insert_pw :
                session.clear()
                session['id'] = request.form['id']
                session['number'] = NUMBER
                login_flag = True
                break

    except mariadb.Error as e:
        print("ERR: {}".format(e))
        sys.exit(1)
    except TypeError as e:
        result = ""
    if conn:
        conn.close()
        # 입력한 ID나 PW 둘 중 하나라도 DB와 일치하지 않은 경우
        result = """
        <script>
        alert("아이디 또는 패스워드를 확인 하세요.");
        </script>
        """
    if login_flag:
        return render_template('/main.html')
    else:
        return render_template('/sign_in.html', content=result)

#로그아웃
@app.route('/sign_out')
def sign_out():
    session.clear()
    return render_template("/main.html")

#회원가입화면
@app.route('/sign_up')
def sign_up():
    return render_template("/sign_up.html")

#회원가입 정보를 DB 입력
@app.route('/sign_up', methods=['POST'])
def member_info_insert():
    new_id = request.form["id"]
    new_pw = request.form["pw"]
    new_name = request.form["name"]
    new_gender = request.form["gender"]
    new_birthday = request.form["birthday"]
    new_phone = request.form["phone"]
    new_email = request.form["email"]

    try:
        conn = get_conn()
        cur = conn.cursor()
        sql = "INSERT INTO MEMBER(id, pw, name, gender, birthday, phone, email) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".format(new_id, new_pw, new_name, new_gender, new_birthday, new_phone, new_email)
        cur.execute(sql)
        conn.commit()

    except mariadb.Error as e:
        print(e)
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template('/sign_in.html')

@app.route('/check_id2', methods=['POST'])
def id_check():
    new_id = request.form["id"]
    result = ""

    try:
        sql = "SELECT id,number FROM MEMBER where id=\'{0}\'".format(new_id)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        for (id, number) in cur:
            result = "{0}".format(id, number)

    except mariadb.Error as e:
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

        if new_id.strip() == result:
            return "사용불가한 ID 입니다."
        else:
            return "사용가능한 ID 입니다."

# 로그인 한 경우 회원정보 불러오기
@app.route('/member_info')
def member_info():
    result = ""

    # 로그인 한 값이 있는 경우 DB에서 해당 정보를 불러오고, 없는 경우 로그인 알림창 뜸.
    if 'number' in session:
        r_num = session['number']
    else:
        result = """
        <script>
        alert("먼저 로그인 하세요.");
        </script>
        """
        return render_template("/main.html", content=result)

    sql = "SELECT NUMBER, ID, PW, PHONE, EMAIL, GENDER, NAME, BIRTHDAY FROM MEMBER WHERE NUMBER = {}".format(r_num)

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        
        result = ""
        for (ID, PW, NAME, GENDER, BIRTHDAY, PHONE, EMAIL, NUMBER) in cur:
            # < input type = "hidden" value = "{0}" >

            result = """      
            <article>
            <div>            
            <ul class=\"box1\">
                <li>아이디 &emsp;&emsp;<input type="text" name="id" required readonly text-align="left" height="40" value="{1}"  class="input_box"></li>
                <li>비밀번호 &emsp;<input type="password" name="pw" required text-align="left" height="40" value="{2}" class="input_box"></li>
            </ul>
            &nbsp;
            </div>
            <div>
                <ul class=\"box2\">
                    <li>이름 &emsp;&emsp;&emsp;<input type="text" name="name" required height="40" value="{6}" class="input_box" ></li>
                    <li>성별 &emsp;&emsp;&emsp;<input type="text" name="gender" required height="40" value="{5}" class="input_box" ></li>
                    <li>생년월일 &emsp;<input type="text" name="birthday" required height="40" value="{7}" class="input_box" ></li>
                    <li>연락처 &emsp;&emsp;<input type="text" name="phone" required height="40" value="{3}" class="input_box"></li>
                    <li>이메일 &emsp;&emsp;<input type="text" name="email" required height="40" value="{4}" class="input_box"></li>
                </ul>
            </div>""".format(ID, PW, NAME, GENDER, BIRTHDAY, PHONE, EMAIL, NUMBER)

    except mariadb.Error as e:
        print(e)
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/member_info.html", content=result)

# 만일 불러온 회원정보에서 수정사항이 있는 경우 수정된 회원정보 DB입력 / ID는 수정불가
@app.route('/member_info', methods=['POST'])
def member_info_modify():
    id = request.form["id"]
    pw = request.form["pw"]
    name = request.form["name"]
    gender = request.form["gender"]
    birth= request.form["birthday"]
    phone = request.form["phone"]
    email = request.form["email"]
    sql = "UPDATE MEMBER SET pw='{0}',name='{1}',gender='{2}',birthday='{3}',phone='{4}',email='{5}' WHERE id='{6}'".format(
        pw, name, gender, birth, phone, email, id)

    print(sql)

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

    except mariadb.Error as e:
        print(e)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/main.html")

@app.route('/game') # 가볍게 즐기는 가위바위보 게임
def game():
    return render_template("/game/game.html")

@app.route('/master/master')
def master_m():
    c_del = request.args.get("delete")
    # delete , None
    conn = get_conn()
    if c_del is not None:
        cur = conn.cursor()
        cur.execute("UPDATE LIBRARY.`MEMBER` SET ID='unknown', PW=1234, PHONE=NULL, EMAIL=NULL, GENDER=NULL, NAME=NULL, BIRTHDAY=NULL WHERE `ID`='{}';".format(c_del))
        conn.commit()


    result = ""
    # 로그인 한 값이 있는 경우 DB에서 해당 정보를 불러오고, 없는 경우 로그인 알림창 뜸.
    if 'number' in session:
        r_num = session['number']
        print(r_num)
    else:
        result = """
        <script>
        alert("관리자만 입장 가능합니다.");
        </script>
        """
        return render_template("/main.html", content=result)

    if r_num == 1: # 마스터계정 번호일경우 접속
        print(1)
    else:
        result = """
        <script>
        alert("관리자만 입장 가능합니다.");
        </script>
        """
        return render_template("/main.html", content=result) 


    sql = "select NAME, ID, PHONE, EMAIL from MEMBER where ID not in('unknown');"
    
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        result = ""

        for (NAME, ID, PHONE, EMAIL) in cur:
            
            result += """
                <tbody>
                    <tr>
                        <td>{1}</td>
                        <td>{0}</td>
                        <td>{2}</td>
                        <td>{3}</td>
                    </tr>
                <tbody>
                """.format(NAME, ID, PHONE, EMAIL)
    except mariadb.Error as e:
        print(e)
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/master/master.html", content=result)


@app.route('/master/community')
def master_c():
    c_del = request.args.get("delete")
    # delete , None
    conn = get_conn()
    if c_del is not None:
        cur = conn.cursor()
        cur.execute("DELETE FROM POST WHERE NUMBER IN ({})".format(c_del))
        conn.commit()

    sql = """
        SELECT m.ID, p.NUMBER, p.title, p.date
        FROM LIBRARY.POST as p
        LEFT join LIBRARY.MEMBER as m
        on p.MEMBER_NUMBER = m.NUMBER ORDER by p.NUMBER desc;
        """
    result = ""

    try:
        cur = conn.cursor()
        cur.execute(sql)

        result += """<table>
                        <thead>
                            <tr>
                                <th>번호</th>
                                <th>제목</th>
                                <th>글쓴이</th>
                                <th>작성일시</th>
                            </tr>
                        </thead>
                    """
        for_rotation_counting = 0
        for (id, number, title, date) in cur:
            for_rotation_counting += 1
            result += """
                        <tr>
                            <th>{1}</th>
                            <th><a href="/community/watch_doc?p.number={4}">{2}</a></th> 
                            <th>{0}</th>
                            <th>{3}</th>
                        </tr>

                        """.format(id, number, title, date, number)

        result += "</table>"
    except mariadb.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/master/community.html", content=result, content1=for_rotation_counting)


@app.route('/master/books', methods=['GET','POST'])
def master_b():
    try:
        conn = get_conn()
        if request.method == 'GET':
            c_del = request.args.get("delete")
            # delete , None    
            if c_del is not None:
                cur = conn.cursor()
                cur.execute("DELETE FROM BOOK WHERE NUMBER IN ({})".format(c_del))
                conn.commit()        
        else:
            book_name = request.form["book_name"]
            book_contents = request.form["book_contents"]
            book_catagory = request.form["book_catagory"]
            file = request.files['book_file']

            sql = """
            INSERT INTO LIBRARY.BOOK 
            (NAME, CONTENTS, CATAGORY_NUMBER, IMG, LOAN) 
            VALUES(
            '{0}',
            '{1}', 
            (SELECT `NUMBER` FROM CATAGORY_BOOK WHERE NAME = '{2}'), 
            '/static/image/books/{3}', 
            'Y'
            )""".format(book_name, book_contents, book_catagory, file.filename)

            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()

            file.save(os.path.join('./static/image/books', file.filename))


        sql = "SELECT NAME, IMG, LOAN, CONTENTS, NUMBER FROM BOOK;"

        cur = conn.cursor()
        cur.execute(sql)

        result = ""

        for (NAME, IMG, LOAN, CONTENTS, NUMBER) in cur:
            result += """
                <div class="book">
                    <input type="image" src="{1}" alt="책" width="100px" height="160px" style="margin-right:15px;">
                    <span id="exa" style="font-size:16px;">{3}</span><br><br>
                    <span style="font-size:18px; color:blue; font-weight: bold;">{0} (책번호 : {4})</span>
                    <span style=font-size:25px;> / <span>
                    <span style="font-size:18px; color:green; font-weight: bold;">대여여부 : </span>
                    <span style=color:red;>{2}</span>
                    <br><br><br>
                </div>
                """.format(NAME, IMG, LOAN, CONTENTS, NUMBER)
        
        sql = "SELECT NUMBER, NAME FROM CATAGORY_BOOK ORDER BY NUMBER "
        cur = conn.cursor()
        cur.execute(sql)

        modal_book_catagory = ""
        for (NUMBER, NAME) in cur:
            modal_book_catagory += """
            <option value="{1}">{1}</option>""".format(NUMBER, NAME)

    except mariadb.Error as e:
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/master/books.html", content=result, catagory_tag=modal_book_catagory)


@app.route('/master/report')
def report():
    result = ""
    # 로그인 한 값이 있는 경우 DB에서 해당 정보를 불러오고, 없는 경우 로그인 알림창 뜸.
    if 'number' in session:
        r_num = session['number']
        print(r_num)
    else:
        result = """
        <script>
        alert("관리자만 입장 가능합니다.");
        </script>
        """
        return render_template("/main.html", content=result)

    if r_num == 1:  # 마스터계정 번호일경우 접속
        print(1)
    else:
        result = """
        <script>
        alert("관리자만 입장 가능합니다.");
        </script>
        """
        return render_template("/main.html", content=result)

    sql = """
    SELECT B.NAME, M.ID, M.NAME AS USER, R.DATE, R.RETURN_DATE 
    FROM RENTER_RECORD R
    JOIN BOOK B
    JOIN MEMBER M
    ON B.NUMBER = R.BOOK_NUMBER
    AND M.NUMBER = R.MEMBER_NUMBER 
    ORDER BY R.DATE
    """

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        result = ""

        for (NAME, ID, USER, DATE, RETURN_DATE) in cur:
            result += """
                <tbody>
                    <tr>
                        <td>{0}</td>
                        <td>{1}</td>
                        <td>{2}</td>
                        <td>{3}</td>
                        <td>{4}</td>
                    </tr>
                <tbody>
                """.format(NAME, ID, USER, DATE, RETURN_DATE)
    except mariadb.Error as e:
        print(e)
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/master/report.html", content=result)

@app.route('/community/board_home')
def board_home():

    sql= """
        SELECT m.ID, p.NUMBER, p.title, p.date
        FROM LIBRARY.POST as p
        LEFT join LIBRARY.MEMBER as m
        on p.MEMBER_NUMBER = m.NUMBER ORDER by p.NUMBER desc;
        """
    result = ""

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        result += """<table>
                        <thead>
                            <tr>
                                <th>번호</th>
                                <th>제목</th>
                                <th>글쓴이</th>
                                <th>작성일시</th>
                            </tr>
                        </thead>
                    """
        for_rotation_counting = 0 # for 문이 회전하는 횟수를 계산해 게시글 수 확인 후 변수에 담아 테이블과 함께 게시판 html에 전달
        for (id, number, title, date) in cur:
            for_rotation_counting +=1
            result += """
                        <tr>
                            <th>{1}</th>
                            <th><a href="/community/watch_doc?p.number={4}">{2}</a></th> 
                            <th>{0}</th>
                            <th>{3}</th>
                        </tr>
                        """.format(id, number, title, date, number)
            # 글 제목에 링크를 걸어 해당 글을 화면 이동

        result += "</table>"

    except mariadb.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


    return render_template("/community/board_home.html", content=result, content1=for_rotation_counting)

# 게시판 홈에서 검색어를 GET방식으로 전달 받아 DB에서 값 수신
@app.route('/community/board_home_search', methods = ["GET"])
def search_doc():
    search_text_val = request.args.get("search_text")

    sql = """
        SELECT p.NUMBER, p.TITLE, m.ID, p.DATE 
        FROM LIBRARY.POST as p left join LIBRARY.MEMBER as m
        on m.NUMBER = p.MEMBER_NUMBER
        where p.TITLE LIKE '%{}%'
        order by p.NUMBER DESC;
        """.format(search_text_val)
    result = ""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        result += """
            <table>
                <thead>
                    <tr>
                        <th>번호</th>
                        <th>제목</th>
                        <th>글쓴이</th>
                        <th>작성일시</th>
                    </tr>
                </thead> """

        for_rotation_counting = 0
        for (number, title, id, date) in cur:
            for_rotation_counting +=1
            result += """
                    <tbody>
                        <tr>
                            <td>{0}</td>
                            <td><a href="/community/watch_doc?p.number={4}">{1}</a></td>
                            <td>{2}</td>
                            <td>{3}</td>
                        </tr>
                    </tbody>
                """.format(number, title, id, date, number)
        result += "</table>"
    except mariadb.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    return render_template("/community/board_home_search.html", content = result, content1 = for_rotation_counting)
    #DB에서 가져온 값을 자동 생성 표에 넣고 이를 담은 변수와 for문의 회전 횟수를 담은 변수를 함께 위 경로에 렌더링

# 사용자가 글을 작성한 후 혹은 본인 글을 수정한 후 넘어오는 함수. 내용을  POST로 받아 온다. 중복 확인할 필요는 없지만 로그인 세션을 한번 더 확인한다.
@app.route('/community/watch_doc', methods=["POST"])
def send_show_doc():

    if 'id' in session:

        try:
            title = request.form["title"]
            contents = request.form["contents"]
            post_file = request.files['post_file']

            if bool(post_file):
                if title == '':
                    alert = """
                            <script>
                                alert("제목을 작성하세요.")
                            </script>
                            """
                    return render_template('/main.html', alert=alert)

                else:

                    try:
                        sql = """
                            SELECT 1 FROM LIBRARY.POST as p
                            left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                            WHERE p.TITLE='{0}' AND p.CONTENTS='{1}' AND m.ID ='{2}';
                        """.format(title, contents, session['id'])

                        conn = get_conn()
                        cur = conn.cursor()
                        cur.execute(sql)

                        check_duple = ()
                        for check_duple in cur:
                            continue

                        # 회원이 동일한 제목과 동일한 내용의 글을 이미 작성한 경우
                        if check_duple ==(1,):
                            result = """
                            <script>
                                alert("이미 동일한 제목과 내용의 글을 작성하셨습니다.")
                            </script>
                            """
                            return render_template('/main.html', alert = result)

                        # 조회한 회원 id 값과 form으로 받은 값들을 db에 전송한다.
                        else:

                            sql = """
                                INSERT INTO LIBRARY.POST
                                (TITLE, MEMBER_NUMBER, POST_FILE, CONTENTS, DATE , VIEW) 
                                VALUES(
                                '{0}',
                                '{1}', 
                                '/static/community/{2}', 
                                '{3}', now(),0);""".format(title, session['number'], post_file.filename, contents)

                            cur = conn.cursor()
                            cur.execute(sql)
                            conn.commit()

                            post_file.save(os.path.join('./static/community', post_file.filename))

                            sql = """
                                    SELECT p.NUMBER FROM LIBRARY.POST as p
                                    where p.MEMBER_NUMBER = {} AND p.TITLE = '{}';
                                    """.format(session['number'], title)

                            cur = conn.cursor()
                            cur.execute(sql)

                            g = ()
                            for g in cur:
                                continue
                            p_number = g[0]

                            # remeber_p_number()에 p_number를 저장
                            check_p_number.insert_p_number(p_number)

                            sql = """ 
                                    SELECT p.TITLE, p.CONTENTS, m.ID , p.POST_FILE, p.DATE, p.MODIFY_DATE, p.NUMBER 
                                    from LIBRARY.POST as p
                                    left join LIBRARY.MEMBER as m
                                    on p.MEMBER_NUMBER = m.NUMBER 
                                    WHERE  p.NUMBER IN (SELECT p.number FROM LIBRARY.POST as p where p.TITLE = '{}' and p.CONTENTS = '{}');
                                """.format(title, contents)
                            cur = conn.cursor()
                            cur.execute(sql)

                            result = ""
                            for (title, contents, id, post_file, date, modify_date, p_number) in cur:
                                modify_date = "수정이력 없음"
                                result +="""
                                        <h3>{0}</h3>
                                        <div class="container">
                                            <p>{1}</p>
                                            <div>
                                                <a class="h_sort" href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>
                                                <p class="h_sort">{7}</p>
                                            </div>
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                            <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                        </div>
                                        <script>
                                            function delete_check_btn(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_doc?p_number={6}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                        """.format(title, contents, id, post_file, date, modify_date, p_number, os.path.basename(post_file))
                            no_com = 0

                    except mariadb.Error as e:
                        print(e)

                    finally:
                        if conn:
                            conn.close()

                    return render_template("/community/watch_doc.html", content= result, no_com = no_com)

            else:
                if title == '':
                    alert = """
                            <script>
                                alert("제목을 작성하세요.")
                            </script>
                            """
                    return render_template('/main.html', alert=alert)

                else:

                    try:
                        sql = """
                            SELECT 1 FROM LIBRARY.POST as p
                            left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                            WHERE p.TITLE='{0}' AND p.CONTENTS='{1}' AND m.ID ='{2}';
                        """.format(title, contents, session['id'])

                        conn = get_conn()
                        cur = conn.cursor()
                        cur.execute(sql)

                        check_duple = ()
                        for check_duple in cur:
                            continue

                        # 회원이 동일한 제목과 동일한 내용의 글을 이미 작성한 경우
                        if check_duple == (1,):
                            result = """
                            <script>
                                alert("이미 동일한 제목과 내용의 글을 작성하셨습니다.")
                            </script>
                            """
                            return render_template('/main.html', alert=result)

                        # 조회한 회원 id 값과 form으로 받은 값들을 db에 전송한다.
                        else:

                            sql = """
                                INSERT INTO LIBRARY.POST
                                (TITLE, MEMBER_NUMBER, CONTENTS, DATE , VIEW) 
                                VALUES(
                                '{0}',
                                '{1}', 
                                '{2}', now(),0);""".format(title, session['number'], contents)

                            cur = conn.cursor()
                            cur.execute(sql)
                            conn.commit()

                            sql = """
                                    SELECT p.NUMBER FROM LIBRARY.POST as p
                                    where p.MEMBER_NUMBER = {} AND p.TITLE = '{}';
                                    """.format(session['number'], title)

                            cur = conn.cursor()
                            cur.execute(sql)

                            g = ()
                            for g in cur:
                                continue
                            p_number = g[0]

                            # remeber_p_number()에 p_number를 저장
                            check_p_number.insert_p_number(p_number)

                            sql = """ 
                                    SELECT p.TITLE, p.CONTENTS, m.ID , p.POST_FILE, p.DATE, p.MODIFY_DATE, p.NUMBER 
                                    from LIBRARY.POST as p
                                    left join LIBRARY.MEMBER as m
                                    on p.MEMBER_NUMBER = m.NUMBER 
                                    WHERE  p.NUMBER IN (SELECT p.number FROM LIBRARY.POST as p where p.TITLE = '{}' and p.CONTENTS = '{}');
                                """.format(title, contents)
                            cur = conn.cursor()
                            cur.execute(sql)

                            result = ""
                            for (title, contents, id, post_file, date, modify_date, p_number) in cur:
                                modify_date = "수정이력 없음"
                                result += """
                                        <h3>{0}</h3>
                                        <div class="container">
                                            <p>{1}</p>
                                            <div>
                                                <a class="h_sort" href ="" download><input type="button" value="첨부파일 다운로드"></a>
                                                <p class="h_sort">{7}</p>
                                            </div>
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                            <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                        </div>
                                        <script>
                                            function delete_check_btn(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_doc?p_number={6}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                        """.format(title, contents, id, post_file, date, modify_date, p_number,"첨부파일 없음")
                            no_com = 0

                    except mariadb.Error as e:
                        print(e)

                    finally:
                        if conn:
                            conn.close()

                    return render_template("/community/watch_doc.html", content=result, no_com=no_com)

        #사용자가 수정한 게시글에서 기존 댓글을 출력한다.
        except:

            amend_title = request.form["amend_title"]
            amend_contents = request.form["amend_contents"]
            amend_post_file = request.files["amend_file"]
            amend_post_number = request.form["amend_p_number"]

            if bool(amend_post_file) == True:

                if bool(amend_title) == False:
                    alert = """
                            <script>
                                alert("제목을 작성하세요.")
                            </script>
                            """
                    return render_template('/main.html', alert=alert)

                else:

                    try:
                        # remeber_p_number()에 amend_post_number를 저장
                        check_p_number.insert_p_number(amend_post_number)

                        sql = """
                                SELECT 1 FROM LIBRARY.POST as p
                                left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                                WHERE p.TITLE='{0}' AND p.CONTENTS='{1}' AND m.ID ='{2}';
                            """.format(amend_title, amend_contents, session['id'])

                        conn = get_conn()
                        cur = conn.cursor()
                        cur.execute(sql)

                        check_duple = ()
                        for check_duple in cur:
                            continue
                        # 회원이 동일한 제목과 동일한 내용의 글을 이미 작성한 경우
                        if check_duple == (1,):
                            result = """
                                    <script>
                                        alert("이미 동일한 제목과 내용의 글을 작성하셨습니다.")
                                    </script>
                                    """
                            return render_template('/main.html', alert=result)
                        else:
                            sql = """
                                UPDATE LIBRARY.POST as p set TITLE ="{0}", CONTENTS ="{1}",
                                POST_FILE ="/static/community/{2}", MODIFY_DATE = now()
                                WHERE p.NUMBER = {3};
                                """.format(amend_title, amend_contents, amend_post_file.filename, amend_post_number)

                            cur = conn.cursor()
                            cur.execute(sql)
                            conn.commit()

                            amend_post_file.save(os.path.join('./static/community', amend_post_file.filename))

                            sql = """
                                    SELECT p.TITLE , p.CONTENTS, m.ID ,p.post_file, p.DATE, p.MODIFY_DATE, p.number
                                    FROM LIBRARY.POST as p
                                    left join LIBRARY.MEMBER as m
                                    on p.MEMBER_NUMBER = m.NUMBER
                                    where p.NUMBER ={};
                                """.format(amend_post_number)

                            cur = conn.cursor()
                            cur.execute(sql)
                            result = ""
                            for (title, contents, id, file, date, modify_date, number) in cur:
                                result += """
                                        <h3>{0}</h3>
                                        <div class="container">
                                            <p>{1}</p>
                                            <div>
                                                <a class="h_sort" href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>
                                                <p class="h_sort">{7}</p>
                                            </div>                            
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                            <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                        </div>
                                        <script>
                                            function delete_check_btn(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_doc?p_number={6}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                        """.format(title, contents, id, file, date, modify_date, number, os.path.basename(file))

                            # 댓글 조회 후 자동 내림차순 정렬
                            sql = """
                                    SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                                    from LIBRARY.COMMENT 
                                    where POST_NUMBER = {};
                                """.format(amend_post_number)
                            conn = get_conn()
                            cur = conn.cursor()
                            cur.execute(sql)

                            comment_result = ""
                            comment_for_rotation_counting = 0
                            for (comment, id, date, c_modify_date, c_number) in cur:
                                comment_for_rotation_counting += 1
                                comment_result += """
                                                    <div class="container">
                                                        <p>{0}</p>
                                                        <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                                        <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                                        <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                                    </div>
                                                    <script>
                                                        function com_delete_check_btn_{4}(){{
                                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                                            window.location = '/community/delete_com?del_c_number={4}';
                                                          }} else{{
                                                            return false;
                                                          }}
                                                       }}
                                                    </script>
                                                """.format(comment, id, date, c_modify_date, c_number)

                    except mariadb.Error as e:
                            print(e)

                    except mariadb.Error as e:
                            print(e)
                            sys.exit(1)
                    finally:
                            if conn:
                                conn.close()

                    return render_template("/community/watch_doc.html", content= result, com_content=comment_result, for_rotation_counting=comment_for_rotation_counting)
            else:

                if bool(amend_title) == False:
                    alert = """
                            <script>
                                alert("제목을 작성하세요.")
                            </script>
                            """
                    return render_template('/main.html', alert=alert)

                # 수정글에 첨부파일이 없는 경우
                else:

                    try:
                        # remeber_p_number()에 amend_post_number를 저장
                        check_p_number.insert_p_number(amend_post_number)

                        sql = """
                                SELECT 1 FROM LIBRARY.POST as p
                                left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                                WHERE p.TITLE='{0}' AND p.CONTENTS='{1}' AND m.ID ='{2}';
                            """.format(amend_title, amend_contents, session['id'])

                        conn = get_conn()
                        cur = conn.cursor()
                        cur.execute(sql)

                        check_duple = ()
                        for check_duple in cur:
                            continue
                        # 회원이 동일한 제목과 동일한 내용의 글을 이미 작성한 경우
                        if check_duple == (1,):
                            result = """
                                    <script>
                                        alert("이미 동일한 제목과 내용의 글을 작성하셨습니다.")
                                    </script>
                                    """
                            return render_template('/main.html', alert=result)
                        else:
                            sql = """
                                UPDATE LIBRARY.POST as p set TITLE ="{0}", CONTENTS ="{1}", MODIFY_DATE = now()
                                WHERE p.NUMBER = {2};
                                """.format(amend_title, amend_contents, amend_post_number)

                            cur = conn.cursor()
                            cur.execute(sql)
                            conn.commit()

                            sql = """
                                    SELECT p.TITLE , p.CONTENTS, m.ID ,p.post_file, p.DATE, p.MODIFY_DATE, p.number
                                    FROM LIBRARY.POST as p
                                    left join LIBRARY.MEMBER as m
                                    on p.MEMBER_NUMBER = m.NUMBER
                                    where p.NUMBER ={};
                                """.format(amend_post_number)

                            cur = conn.cursor()
                            cur.execute(sql)
                            result = ""
                            for (title, contents, id, file, date, modify_date, number) in cur:
                                result += """
                                        <h3>{0}</h3>
                                        <div class="container">
                                            <p>{1}</p>
                                            <div>
                                                <a class="h_sort" href ="" disabled download><input type="button" value="첨부파일 다운로드"></a>
                                                <p class="h_sort">{7}</p>
                                            </div>                            
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                            <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                        </div>
                                        <script>
                                            function delete_check_btn(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_doc?p_number={6}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                        """.format(title, contents, id, file, date, modify_date, number,"첨부파일 없음")

                            # 댓글 조회 후 자동 내림차순 정렬
                            sql = """
                                    SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                                    from LIBRARY.COMMENT 
                                    where POST_NUMBER = {};
                                """.format(amend_post_number)
                            conn = get_conn()
                            cur = conn.cursor()
                            cur.execute(sql)

                            comment_result = ""
                            comment_for_rotation_counting = 0
                            for (comment, id, date, c_modify_date, c_number) in cur:
                                comment_for_rotation_counting += 1
                                comment_result += """
                                                    <div class="container">
                                                        <p>{0}</p>
                                                        <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                                        <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                                        <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                                    </div>
                                                    <script>
                                                        function com_delete_check_btn_{4}(){{
                                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                                            window.location = '/community/delete_com?del_c_number={4}';
                                                          }} else{{
                                                            return false;
                                                          }}
                                                       }}
                                                    </script>
                                                """.format(comment, id, date, c_modify_date, c_number)

                    except mariadb.Error as e:
                        print(e)

                    except mariadb.Error as e:
                        print(e)
                        sys.exit(1)
                    finally:
                        if conn:
                            conn.close()

                    return render_template("/community/watch_doc.html", content=result, com_content=comment_result,
                                           for_rotation_counting=comment_for_rotation_counting)


@app.route('/community/watch_doc', methods = ["GET"])
def watch_doc():
    post_number_temp_bang = request.args.get("p.number")
    # remeber_p_number()에 p.number를 저장
    check_p_number.insert_p_number(post_number_temp_bang)

    result = ""

    sql = """
        SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
        p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
        left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
        WHERE p.NUMBER = {};
        """.format(post_number_temp_bang)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql)

    i = []
    for i in cur:
        continue

    if bool(i[2]) == True:

        try:
            sql = """
                    SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                    p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                    left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                    WHERE p.NUMBER = {};
                    """.format(post_number_temp_bang)

            cur = conn.cursor()
            cur.execute(sql)

            for (title, contents, file, id, date, modify_date,p_number) in cur:
                if modify_date == None:
                    modify_date = "None"

                    result += """
                            <h3>{0}</h3>
                            <div class="container">
                                <p>{1}</p>
                                <div>
                                    <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                    <p class="h_sort">{7}</p>
                                </div>                                 
                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                            </div>
                            <script>
                                function delete_check_btn(){{
                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                    window.location = '/community/delete_doc?p_number={6}';
                                  }} else{{
                                    return false;
                                  }}
                               }}
                            </script>
                            """.format(title, contents, file, id, date, modify_date, p_number, os.path.basename(file))
                else:
                    result += """
                            <h3>{0}</h3>
                            <div class="container">
                                <p>{1}</p>
                                <div>
                                    <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                    <p class="h_sort">{7}</p>
                                </div>                                
                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                            </div>
                            <script>
                                function delete_check_btn(){{
                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                    window.location = '/community/delete_doc?p_number={6}';
                                  }} else{{
                                    return false;
                                  }}
                               }}
                            </script>
                            """.format(title, contents, file, id, date, modify_date, p_number, os.path.basename(file))


            sql = """
                    SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                    from LIBRARY.COMMENT 
                    where POST_NUMBER = {};
                """.format(post_number_temp_bang)

            cur = conn.cursor()
            cur.execute(sql)

            comment_result = ""
            comment_for_rotation_counting = 0
            for (comment, id, date, c_modify_date, c_number) in cur:
                comment_for_rotation_counting += 1
                comment_result += """
                                <div class="container">
                                    <p>{0}</p>
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                    <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                    <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                </div>
                                <script>
                                    function com_delete_check_btn_{4}(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_com?del_c_number={4}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                            """.format(comment, id, date, c_modify_date, c_number)

        except mariadb.Error as e:
            print(e)

        finally:
            if conn:
                conn.close()

        return render_template("/community/watch_doc.html", content= result, com_content = comment_result, for_rotation_counting = comment_for_rotation_counting)
        #연산한 결과를 watch_doc.html에서 전달 받아 이를 출력
    
    else:
        try:
            sql = """
                    SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                    from LIBRARY.COMMENT 
                    where POST_NUMBER = {};
                """.format(post_number_temp_bang)

            cur = conn.cursor()
            cur.execute(sql)

            comment_result = ""
            comment_for_rotation_counting = 0
            for (comment, id, date, c_modify_date, c_number) in cur:
                comment_for_rotation_counting += 1
                comment_result += """
                                    <div class="container">
                                        <p>{0}</p>
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                        <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                        <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                    </div>
                                    <script>
                                        function com_delete_check_btn_{4}(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_com?del_c_number={4}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                """.format(comment, id, date, c_modify_date, c_number)

            sql = """
                SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                WHERE p.NUMBER = {};
                """.format(post_number_temp_bang)

            cur = conn.cursor()
            cur.execute(sql)

            result = ''
            for (title, contents, file, id, date, modify_date,p_number) in cur:
                if modify_date == None:
                    modify_date = "None"

                    result += """
                            <h3>{0}</h3>
                            <div class="container">
                                <p>{1}</p>
                                <!-- <div>
                                      <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                      <p class="h_sort">{7}</p>
                                  </div>                                  -->                             
                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                            </div>
                            <script>
                                function delete_check_btn(){{
                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                    window.location = '/community/delete_doc?p_number={6}';
                                  }} else{{
                                    return false;
                                  }}
                               }}
                            </script>
                            """.format(title, contents, file, id, date, modify_date, p_number, "첨부파일 없음")
                else:
                    result += """
                            <h3>{0}</h3>
                            <div class="container">
                                <p>{1}</p>
                                <!-- <div>
                                      <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                      <p class="h_sort">{7}</p>
                                  </div>                                  -->                          
                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                            </div>
                            <script>
                                function delete_check_btn(){{
                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                    window.location = '/community/delete_doc?p_number={6}';
                                  }} else{{
                                    return false;
                                  }}
                               }}
                            </script>
                            """.format(title, contents, file, id, date, modify_date, p_number, "첨부파일 없음")

        except mariadb.Error as e:
            print(e)

        finally:
            if conn:
                conn.close()

        return render_template("/community/watch_doc.html", content= result, com_content = comment_result, for_rotation_counting = comment_for_rotation_counting)
        #연산한 결과를 watch_doc.html에서 전달 받아 이를 출력


@app.route('/community/write_doc')#사용자가 글 작성 메뉴를 클릭하면 이동되는 화면
def write_doc():
    author = session['id']
    return render_template("/community/write_doc.html", author = author)

@app.route('/community/amend_doc', methods = ['GET'])
# 사용자가 게시글에 수정 버튼을 클릭하면 실행되는 함수, 글 번호를 GET방식으로 전달받는다.
def amend_doc():
    p_number = request.args.get("p_number")
    if 'id' in session:

        sql = """
            SELECT m.ID from LIBRARY.POST as p
            left join LIBRARY.MEMBER as m
            on p.MEMBER_NUMBER = m.NUMBER 
            WHERE  p.NUMBER = '{}';
            """.format(p_number)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        for data in cur:
            continue

        if data[0] == session['id']:

            sql = """ 
                    SELECT p.title, p.CONTENTS, p.post_file, p.NUMBER FROM LIBRARY.POST as p
                    WHERE p.NUMBER = {};
                    """.format(p_number)
            result = ""
            # 수정에 필요한 모든 값들을 쿼리문으로 불러옴.
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)

                for (title, contents, file, p_number) in cur:
                    result += """ 
                            <form action="/community/watch_doc" method="POST" enctype="multipart/form-data">
                                <p>제목</p>
                                <br>
                                <input type="text" name= "amend_title" value="{0}">
                                <br>
                                <textarea rows="30" style="width: 100%; resize: none;" name="amend_contents">{1}</textarea>
                                <input type="hidden" name="amend_p_number" value="{3}">
                                <br>
                                <div>
                                    <p>파일첨부 :</p><input type="file" name="amend_file">
                                    <input style ="float:right" type="submit" value="저장" onclick="">
                                </div>
                            </form>
                                """.format(title, contents, file, p_number)

            except mariadb.Error as e:
                print(e)
            finally:
                if conn:
                    conn.close()

            return render_template("/community/watch_doc_amend.html", content_amend=result)
            # 실행결과를 watch_doc_amend.html에 변수에 담아 전달

        # 로그인한 사용자가 해당 글을 작성하지 않은 경우
        else:
            sql = """
                    SELECT p.POST_FILE from LIBRARY.POST as p
                    where p.NUMBER ={};
                    """.format(p_number)
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(sql)

            i = ()
            for i in cur:
                continue

            if bool(i[0]) == True:

                try:
                    alert = """
                        <script>
                            alert("수정 권한이 없습니다.")
                        </script>
                    """

                    #  댓글, 게시글(파일 다운로드 포함) 추가

                    sql = """
                            SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                            from LIBRARY.COMMENT 
                            where POST_NUMBER = {};
                        """.format(p_number)
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    comment_result = ""
                    comment_for_rotation_counting = 0
                    for (comment, id, date, c_modify_date, c_number) in cur:
                        comment_for_rotation_counting += 1
                        comment_result += """
                                            <div class="container">
                                                <p>{0}</p>
                                                <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                                <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                                <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                            </div>
                                            <script>
                                                function com_delete_check_btn_{4}(){{
                                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                                    window.location = '/community/delete_com?del_c_number={4}';
                                                  }} else{{
                                                    return false;
                                                  }}
                                               }}
                                            </script>
                                        """.format(comment, id, date, c_modify_date, c_number)



                    sql = """
                            SELECT p.TITLE , p.CONTENTS, m.ID ,p.POST_FILE, p.DATE, p.MODIFY_DATE, p.NUMBER 
                            FROM LIBRARY.POST as p
                            left join LIBRARY.MEMBER as m
                            on p.MEMBER_NUMBER = m.NUMBER
                            where p.NUMBER ={};
                            """.format(p_number)
                    result = ""

                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    result = ""
                    for (title, contents, id, post_file, date, modify_date, p_number) in cur:
                        if modify_date == None:
                            modify_date = "수정이력 없음"
                            result += """
                                        <h3>{0}</h3>
                                        <div class="container">
                                            <p>{1}</p>
                                            <div>
                                                <a class="h_sort" href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>
                                                <p class="h_sort">{7}</p>
                                            </div>                         
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                            <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                        </div>
                                        <script>
                                            function delete_check_btn(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_doc?p_number={6}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                        """.format(title, contents, id, post_file, date, modify_date, p_number,
                                                   os.path.basename(post_file))
                        else:
                            result += """
                                        <h3>{0}</h3>
                                        <div class="container">
                                            <p>{1}</p>
                                            <div>
                                                <a class="h_sort" href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>
                                                <p class="h_sort">{7}</p>
                                            </div>                            
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                            <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                        </div>
                                        <script>
                                            function delete_check_btn(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_doc?p_number={6}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                        """.format(title, contents, id, post_file, date, modify_date,
                                                   p_number, os.path.basename(post_file))
                except mariadb.Error as e:
                    print(e)
                finally:
                    if conn:
                        conn.close()

                return render_template('/community/watch_doc.html', content=result, alert=alert, com_content=comment_result, for_rotation_counting=comment_for_rotation_counting)

            else:

                try:
                    alert = """
                        <script>
                            alert("수정 권한이 없습니다.")
                        </script>
                    """

                    #  댓글, 게시글(파일 다운로드 포함) 추가

                    sql = """
                            SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                            from LIBRARY.COMMENT 
                            where POST_NUMBER = {};
                        """.format(p_number)
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    comment_result = ""
                    comment_for_rotation_counting = 0
                    for (comment, id, date, c_modify_date, c_number) in cur:
                        comment_for_rotation_counting += 1
                        comment_result += """
                                            <div class="container">
                                                <p>{0}</p>
                                                <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                                <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                                <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                            </div>
                                            <script>
                                                function com_delete_check_btn_{4}(){{
                                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                                    window.location = '/community/delete_com?del_c_number={4}';
                                                  }} else{{
                                                    return false;
                                                  }}
                                               }}
                                            </script>
                                        """.format(comment, id, date, c_modify_date, c_number)

                    sql = """
                            SELECT p.TITLE , p.CONTENTS, m.ID ,p.POST_FILE, p.DATE, p.MODIFY_DATE, p.NUMBER 
                            FROM LIBRARY.POST as p
                            left join LIBRARY.MEMBER as m
                            on p.MEMBER_NUMBER = m.NUMBER
                            where p.NUMBER ={};
                            """.format(p_number)
                    result = ""

                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    result = ""
                    for (title, contents, id, post_file, date, modify_date, p_number) in cur:
                        if modify_date == None:
                            modify_date = "수정이력 없음"
                            result += """
                                        <h3>{0}</h3>
                                        <div class="container">
                                            <p>{1}</p>
                                            <!-- <div>
                                                  <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                  <p class="h_sort">{7}</p>
                                              </div>                                  -->                    
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                            <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                        </div>
                                        <script>
                                            function delete_check_btn(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_doc?p_number={6}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                        """.format(title, contents, id, post_file, date, modify_date, p_number,"첨부파일 없음")
                        else:
                            result += """
                                        <h3>{0}</h3>
                                        <div class="container">
                                            <p>{1}</p>
                                            <!-- <div>
                                                  <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                  <p class="h_sort">{7}</p>
                                              </div>                                  -->                        
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                            <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                        </div>
                                        <script>
                                            function delete_check_btn(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_doc?p_number={6}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                        """.format(title, contents, id, post_file, date, modify_date, p_number, "첨부파일 없음")
                except mariadb.Error as e:
                    print(e)
                finally:
                    if conn:
                        conn.close()

                return render_template('/community/watch_doc.html', content=result, alert=alert, com_content=comment_result, for_rotation_counting=comment_for_rotation_counting)

    # 로그인 하지 않고 수정 버튼 누른 경우
    else:
        alert = """
                <script>
                    alert("로그인을 먼저 하세요.")
                </script>
                """

        return render_template('/sign_in.html', alert=alert)

# 사용자가 게시글 삭제 버튼을 누르고 alert 창에서 확인 버튼을 누르면 넘어오는 함수. GET방식으로 p_number 값이 함께 넘어온다.
@app.route('/community/delete_doc', methods = ["GET"])
def delete_query():
    p_number = request.args.get("p_number")
    if 'id' in session:

        sql = """
            SELECT m.ID from LIBRARY.POST as p
            left join LIBRARY.MEMBER as m
            on p.MEMBER_NUMBER = m.NUMBER 
            WHERE  p.NUMBER = '{}';
            """.format(p_number)
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        #data = ()
        for data in cur:
            continue

        if data[0] == session['id']:
            try:

                sql = """
                    SELECT COMMENT_NUMBER from LIBRARY.COMMENT
                    where POST_NUMBER = {0};
                    """.format(p_number)

                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)

                x = ()

                for x in cur:
                    continue

                if bool(x) == True:
                    # sql = """
                    #     SELECT COMMENT_NUMBER FROM LIBRARY.COMMENT
                    #     where POST_NUMBER = {};
                    # """.format(p_number)
                    # conn = get_conn()
                    # cur = conn.cursor()
                    # cur.execute(sql)
                    #
                    # d_progresss = []
                    # for i in cur:
                    #     d_progresss.append(i)
                    #
                    # for u in range(len(d_progresss)):
                    #     sql = """
                    #         DELETE FROM LIBRARY.COMMENT
                    #         where COMMENT_NUMBER ={};
                    #     """.format(int(d_progresss[u][0]))
                    #
                    #     cur = conn.cursor()
                    #     cur.execute(sql)
                    #     conn.commit()
                    # sql = """
    #                         DELETE FROM LIBRARY.POST
    #                         where `NUMBER` = {};
    #                         """.format(p_number)
                    # cur = conn.cursor()
                    # cur.execute(sql)
                    # conn.commit()
                    alert = """
                        <script>
                            alert("해당 글에는 댓글이 달려 있어 삭제가 불가합니다.")
                        </script>
                        """
                    sql = """
                                SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                                p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                                left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                                WHERE p.NUMBER = {};
                                """.format(p_number)

                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    for (title, contents, file, id, date, modify_date, p_number) in cur:
                        result = ""
                        if modify_date == None:
                            modify_date = "None"

                            result += """
                                    <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <a href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>                              
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?p_number={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, file, id, date, modify_date, p_number)
                        else:
                            result = ""
                            result += """
                                        <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <a href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>                              
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?p_number={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, file, id, date, modify_date, p_number)

                    sql = """
                        SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                        from LIBRARY.COMMENT 
                        where POST_NUMBER = {};
                    """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    comment_result = ""
                    comment_for_rotation_counting = 0
                    for (comment, id, date, c_modify_date, c_number) in cur:
                        comment_for_rotation_counting += 1
                        comment_result += """
                                            <div class="container">
                                                <p>{0}</p>
                                                <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                                <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                                <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                            </div>
                                            <script>
                                                function com_delete_check_btn_{4}(){{
                                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                                    window.location = '/community/delete_com?del_c_number={4}';
                                                  }} else{{
                                                    return false;
                                                  }}
                                               }}
                                            </script>
                                        """.format(comment, id, date, c_modify_date, c_number)
                    return render_template('community/watch_doc.html', content = result, com_content = comment_result, for_rotation_counting = comment_for_rotation_counting, alert = alert)

                else:
                    sql = """
                            DELETE FROM LIBRARY.POST where NUMBER = {} ;
                           """.format(p_number)
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)
                    conn.commit()
                    sql = """
                            SELECT m.ID, p.NUMBER, p.title, p.date
                            FROM LIBRARY.POST as p
                            LEFT join LIBRARY.MEMBER as m
                            on p.MEMBER_NUMBER = m.NUMBER ORDER by p.NUMBER desc;
                            """
                    result = ""

                    cur = conn.cursor()
                    cur.execute(sql)

                    result += """<table>
                                        <thead>
                                            <tr>
                                                <th>번호</th>
                                                <th>제목</th>
                                                <th>글쓴이</th>
                                                <th>작성일시</th>
                                            </tr>
                                        </thead>
                                    """
                    for_rotation_counting = 0  # for 문이 회전하는 횟수를 계산해 게시글 수 확인 후 변수에 담아 테이블과 함께 게시판 html에 전달
                    for (id, number, title, date) in cur:
                        for_rotation_counting += 1
                        result += """
                                        <tr>
                                            <th>{1}</th>
                                            <th><a href="/community/watch_doc?p.number={4}">{2}</a></th> 
                                            <th>{0}</th>
                                            <th>{3}</th>
                                        </tr>
            
                                        """.format(id, number, title, date, number)
                        # 글 제목에 링크를 걸어 해당 글을 화면 이동

                    result += "</table>"

            except mariadb.Error as e:
                print(e)
            finally:
                if conn:
                    conn.close()

            return render_template("/community/board_home.html", content=result, content1 = for_rotation_counting)
        # 로그인한 사용자가 다른 사용자의 글을 삭제하려는 경우

        else:
            alert = """
                    <script>
                        alert("삭제 권한이 없습니다.")
                    </script>
                """
            sql = """
                    SELECT p.POST_FILE from LIBRARY.POST as p
                    where p.NUMBER ={};
                    """.format(p_number)
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(sql)

            i = ()
            for i in cur:
                continue

            if bool(i[0]) == True:

                try:
                    sql = """
                            SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                            from LIBRARY.COMMENT 
                            where POST_NUMBER = {};
                        """.format(p_number)
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    comment_result = ""
                    comment_for_rotation_counting = 0
                    for (comment, id, date, c_modify_date, c_number) in cur:
                        comment_for_rotation_counting += 1
                        comment_result += """
                                        <div class="container">
                                            <p>{0}</p>
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                            <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                            <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                        </div>
                                        <script>
                                            function com_delete_check_btn_{4}(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_com?del_c_number={4}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                    """.format(comment, id, date, c_modify_date, c_number)

                    sql = """
                            SELECT p.TITLE , p.CONTENTS, m.ID ,p.POST_FILE, p.DATE, p.MODIFY_DATE, p.NUMBER 
                            FROM LIBRARY.POST as p
                            left join LIBRARY.MEMBER as m
                            on p.MEMBER_NUMBER = m.NUMBER
                            where p.NUMBER ={};
                            """.format(p_number)
                    result = ""

                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    result = ""
                    for (title, contents, id, post_file, date, modify_date, p_number) in cur:
                        if modify_date == None:
                            modify_date = "수정이력 없음"
                            result += """
                                        <h3>{0}</h3>
                                        <div class="container">
                                            <p>{1}</p>
                                            <div>
                                                <a class="h_sort" href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>
                                                <p class="h_sort">{7}</p>
                                            </div>                         
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                            <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                        </div>
                                        <script>
                                            function delete_check_btn(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_doc?p_number={6}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                        """.format(title, contents, id, post_file, date, modify_date, p_number, os.path.basename(post_file))
                        else:
                            result += """
                                    <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <div>
                                            <a class="h_sort" href ="{3}" download><input type="button" value="첨부파일 다운로드"></a>
                                            <p class="h_sort">{7}</p>
                                        </div>                            
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?p_number={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, id, post_file, date, modify_date, p_number, os.path.basename(post_file))
                except mariadb.Error as e:
                    print(e)
                finally:
                    if conn:
                        conn.close()

                return render_template('/community/watch_doc.html', content=result, alert=alert, com_content=comment_result, for_rotation_counting=comment_for_rotation_counting)

            else:

                try:
                    sql = """
                            SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                            from LIBRARY.COMMENT 
                            where POST_NUMBER = {};
                        """.format(p_number)
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    comment_result = ""
                    comment_for_rotation_counting = 0
                    for (comment, id, date, c_modify_date, c_number) in cur:
                        comment_for_rotation_counting += 1
                        comment_result += """
                                            <div class="container">
                                                <p>{0}</p>
                                                <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                                <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                                <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                            </div>
                                            <script>
                                                function com_delete_check_btn_{4}(){{
                                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                                    window.location = '/community/delete_com?del_c_number={4}';
                                                  }} else{{
                                                    return false;
                                                  }}
                                               }}
                                            </script>
                                        """.format(comment, id, date, c_modify_date, c_number)

                    sql = """
                            SELECT p.TITLE , p.CONTENTS, m.ID ,p.POST_FILE, p.DATE, p.MODIFY_DATE, p.NUMBER 
                            FROM LIBRARY.POST as p
                            left join LIBRARY.MEMBER as m
                            on p.MEMBER_NUMBER = m.NUMBER
                            where p.NUMBER ={};
                            """.format(p_number)
                    result = ""

                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(sql)

                    result = ""
                    for (title, contents, id, post_file, date, modify_date, p_number) in cur:
                        if modify_date == None:
                            modify_date = "수정이력 없음"
                            result += """
                                    <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <!-- <div>
                                              <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                              <p class="h_sort">{7}</p>
                                          </div>                                  -->                    
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?p_number={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, id, post_file, date, modify_date,
                                               p_number, "첨부파일 없음")
                        else:
                            result += """
                                    <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <!-- <div>
                                              <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                              <p class="h_sort">{7}</p>
                                          </div>                                  -->                        
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {2} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?p_number={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, id, post_file, date, modify_date,
                                               p_number, "첨부파일 없음")
                except mariadb.Error as e:
                    print(e)
                finally:
                    if conn:
                        conn.close()

                return render_template('/community/watch_doc.html', content=result, alert=alert, com_content=comment_result, for_rotation_counting=comment_for_rotation_counting)

    # 비 로그인 상태
    else:
        alert = """
                <script>
                    alert("로그인되지 않았습니다. 먼저 회원가입 혹은 로그인을 하세요.")
                </script>
                """
        return render_template('/sign_in.html', alert=alert)

#댓글을 작성하거나 수정(수정 내용 작성 후)했을 경우 넘어오는 경로. POST로 내용을 전달 받는다.
@app.route('/community/write_com', methods = ["POST"])
def write_com():
    if 'id' in session:
        try:
            comment_temp = request.form["comment"]

            try:
                p_number = check_p_number.return_p_number() # 클래스로 게시글 번호 가져옴.
                p_number = int(p_number)
                id_temp = session['id']
                m_number = session['number']

                sql = """
                        SELECT 1 from LIBRARY.COMMENT c
                        where c.COMMENT = '{0}' and c.MEMBER_ID = '{1}' and c.POST_NUMBER = {2}; 
                    """.format(comment_temp, id_temp, p_number)
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)

                i = ()
                for i in cur:
                    continue
                if i == (1,):
                    result = """
                            <script>
                                alert("해당 글에 이미 같은 내용의 댓글을 달았습니다.") 
                            </script>
                            """
                    if conn:
                        conn.close()
                    return render_template('/main.html', alert=result)

                else:
                    sql = """
                            insert into LIBRARY.COMMENT (COMMENT, MEMBER_ID, DATE, MEMBER_NUMBER, POST_NUMBER) 
                            values ('{0}', '{1}', now(), {2}, {3});
                        """.format(comment_temp, id_temp, m_number, p_number)

                    cur = conn.cursor()
                    cur.execute(sql)
                    conn.commit()

                    # 댓글 조회 후 자동 내림차순 정렬
                    sql = """
                            SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                            from LIBRARY.COMMENT 
                            where POST_NUMBER = {};
                        """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    comment_result = ""
                    comment_for_rotation_counting = 0
                    for (comment, id, date, c_modify_date, c_number) in cur:
                        comment_for_rotation_counting += 1
                        comment_result += """
                                            <div class="container">
                                                <p>{0}</p>
                                                <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                                <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                                <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                            </div>
                                            <script>
                                                function com_delete_check_btn_{4}(){{
                                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                                    window.location = '/community/delete_com?del_c_number={4}';
                                                  }} else{{
                                                    return false;
                                                  }}
                                               }}
                                            </script>
                                        """.format(comment, id, date, c_modify_date, c_number)
                    sql = """
                           SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                           p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                           left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                           WHERE p.NUMBER = {};
                           """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    i = []
                    for i in cur:
                        continue

                    if bool(i[2]) == True:
                        sql = """
                           SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                           p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                           left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                           WHERE p.NUMBER = {};
                           """.format(p_number)

                        cur = conn.cursor()
                        cur.execute(sql)

                        for (title, contents, file, id, date, modify_date, p_number) in cur:
                            if modify_date == None:
                                modify_date = "None"
                                result = ''
                                result += """
                                            <h3>{0}</h3>
                                            <div class="container">
                                                <p>{1}</p>
                                                <div>
                                                    <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                    <p class="h_sort">{7}</p>
                                                </div>                                 
                                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                            </div>
                                            <script>
                                                function delete_check_btn(){{
                                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                                    window.location = '/community/delete_doc?p_number={6}';
                                                  }} else{{
                                                    return false;
                                                  }}
                                               }}
                                            </script>
                                            """.format(title, contents, file, id, date, modify_date,p_number, os.path.basename(file))
                            else:
                                result += """
                                        <h3>{0}</h3>
                                        <div class="container">
                                            <p>{1}</p>
                                            <div>
                                                <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                <p class="h_sort">{7}</p>
                                            </div>                                
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                            <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                        </div>
                                        <script>
                                            function delete_check_btn(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_doc?p_number={6}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                        """.format(title, contents, file, id, date, modify_date, p_number, os.path.basename(file))
                    else:
                        sql = """
                                SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                                p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                                left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                                WHERE p.NUMBER = {};
                                """.format(p_number)

                        cur = conn.cursor()
                        cur.execute(sql)

                        for (title, contents, file, id, date, modify_date, p_number) in cur:
                            if modify_date == None:
                                modify_date = "None"
                                result = ''
                                result += """
                                        <h3>{0}</h3>
                                        <div class="container">
                                            <p>{1}</p>
                                            <!-- <div>
                                                  <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                  <p class="h_sort">{7}</p>
                                              </div>                                  -->                             
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                            <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                            <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                        </div>
                                        <script>
                                            function delete_check_btn(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_doc?p_number={6}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                        """.format(title, contents, file, id, date, modify_date, p_number,"첨부파일 없음")
                            else:
                                result += """
                                    <h3>{0}</h3>
                                    <div class="container">
                                        <p>{1}</p>
                                        <!-- <div>
                                              <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                              <p class="h_sort">{7}</p>
                                          </div>                                  -->                           
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                        <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                        <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                    </div>
                                    <script>
                                        function delete_check_btn(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_doc?p_number={6}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                    """.format(title, contents, file, id, date, modify_date, p_number, "첨부파일 없음")
            except mariadb.Error as e:
                print(e)
                sys.exit(1)
            except TypeError as e:
                print(e)
            if conn:
                conn.close()
                
            return render_template('/community/watch_doc.html', com_content=comment_result, for_rotation_counting=comment_for_rotation_counting, content = result)

        except:

            try:
                amend_comment = request.form["amend_com"]
                amend_c_number = request.form["amend_c_number"]

                sql = """
                    SELECT c.MEMBER_ID, c.POST_NUMBER from LIBRARY.COMMENT c
                    where c.COMMENT_NUMBER = {};
                """.format(amend_c_number)

                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)

                data_temp = ()
                for data_temp in cur:
                    continue
                amend_com_id = data_temp[0]
                amend_com_p_number = data_temp[1]
                amend_com_p_number = int(amend_com_p_number)

                sql="""
                    SELECT 1 FROM LIBRARY.COMMENT c where 
                    c.POST_NUMBER = {0}
                    and c.COMMENT ="{1}"
                    AND c.MEMBER_ID ='{2}';
                    """.format(amend_com_p_number, amend_comment, amend_com_id)

                cur = conn.cursor()
                cur.execute(sql)

                i_temp = ()
                for i_temp in cur:
                    continue

                if i_temp == False:
                    result = """
                        <script>
                            alert("해당 글에 이미 같은 내용의 댓글을 작성했습니다.")
                        </script>
                        """
                    if conn:
                        conn.close

                    return render_template('/main.html', alert=result)
                else:

                    sql = """
                        UPDATE LIBRARY.COMMENT as c 
                        set c.COMMENT = '{0}', c.MODIFY_DATE =now()
                        WHERE c.COMMENT_NUMBER = {1};
                        """.format(amend_comment, amend_c_number)

                    cur=conn.cursor()
                    cur.execute(sql)
                    conn.commit()

                    sql = """
                        SELECT p.NUMBER
                        from LIBRARY.POST as p
                        where p.`NUMBER` = (SELECT c.POST_NUMBER from LIBRARY.COMMENT as c
                        where c.COMMENT_NUMBER ={});
                    """.format(amend_c_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    j = ()
                    for j in cur:
                        continue
                    p_number = j[0]
                    p_number = int(p_number)

                    #댓글 조회후 자동 정렬
                    sql = """
                        SELECT c.COMMENT, c.MEMBER_ID, c.`DATE` , c.MODIFY_DATE, c.COMMENT_NUMBER
                        FROM LIBRARY.COMMENT as c
                        where c.POST_NUMBER = {};
                    """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    comment_result = ""
                    comment_for_rotation_counting = 0
                    for (comment, id, date, c_modify_date, c_number) in cur:
                        comment_for_rotation_counting += 1
                        comment_result += """
                                        <div class="container">
                                            <p>{0}</p>
                                            <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                            <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                            <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                        </div>
                                        <script>
                                            function com_delete_check_btn_{4}(){{
                                              if(confirm("정말 삭제하시겠습니까?")==true){{
                                                window.location = '/community/delete_com?del_c_number={4}';
                                              }} else{{
                                                return false;
                                              }}
                                           }}
                                        </script>
                                    """.format(comment, id, date, c_modify_date, c_number)

                    sql = """
                       SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                       p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                       left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                       WHERE p.NUMBER = {};
                       """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    i = []
                    for i in cur:
                        continue

                    if bool(i[2]) == True:
                        sql = """
                           SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                           p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                           left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                           WHERE p.NUMBER = {};
                           """.format(p_number)

                        cur = conn.cursor()
                        cur.execute(sql)

                        for (title, contents, file, id, date, modify_date, p_number) in cur:
                            if modify_date == None:
                                modify_date = "None"

                                result = ''
                                result += """
                                            <h3>{0}</h3>
                                            <div class="container">
                                                <p>{1}</p>
                                                <div>
                                                    <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                    <p class="h_sort">{7}</p>
                                                </div>                                 
                                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                            </div>
                                            <script>
                                                function delete_check_btn(){{
                                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                                    window.location = '/community/delete_doc?p_number={6}';
                                                  }} else{{
                                                    return false;
                                                  }}
                                               }}
                                            </script>
                                            """.format(title, contents, file, id, date, modify_date, p_number,
                                                       os.path.basename(file))
                            else:
                                result += """
                                            <h3>{0}</h3>
                                            <div class="container">
                                                <p>{1}</p>
                                                <div>
                                                    <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                    <p class="h_sort">{7}</p>
                                                </div>                                
                                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                            </div>
                                            <script>
                                                function delete_check_btn(){{
                                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                                    window.location = '/community/delete_doc?p_number={6}';
                                                  }} else{{
                                                    return false;
                                                  }}
                                               }}
                                            </script>
                                            """.format(title, contents, file, id, date, modify_date, p_number,
                                                       os.path.basename(file))
                    else:
                        sql = """
                                SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                                p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                                left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                                WHERE p.NUMBER = {};
                                """.format(p_number)

                        cur = conn.cursor()
                        cur.execute(sql)

                        result = ''
                        for (title, contents, file, id, date, modify_date, p_number) in cur:
                            if modify_date == None:
                                modify_date = "None"

                                result += """
                                            <h3>{0}</h3>
                                            <div class="container">
                                                <p>{1}</p>
                                                <!-- <div>
                                                      <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                      <p class="h_sort">{7}</p>
                                                  </div>                                  -->                          
                                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                            </div>
                                            <script>
                                                function delete_check_btn(){{
                                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                                    window.location = '/community/delete_doc?p_number={6}';
                                                  }} else{{
                                                    return false;
                                                  }}
                                               }}
                                            </script>
                                            """.format(title, contents, file, id, date, modify_date, p_number,
                                                       "첨부파일 없음")
                            else:
                                result += """
                                            <h3>{0}</h3>
                                            <div class="container">
                                                <p>{1}</p>
                                                <!-- <div>
                                                      <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                      <p class="h_sort">{7}</p>
                                                  </div>                                  -->                              
                                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                            </div>
                                            <script>
                                                function delete_check_btn(){{
                                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                                    window.location = '/community/delete_doc?p_number={6}';
                                                  }} else{{
                                                    return false;
                                                  }}
                                               }}
                                            </script>
                                            """.format(title, contents, file, id, date, modify_date, p_number,
                                                       "첨부파일 없음")
            except mariadb.Error as e:
                print(e)
                sys.exit(1)
            except TypeError as e:
                print(e)
            if conn:
                conn.close()

            return render_template('/community/watch_doc.html', com_content=comment_result, for_rotation_counting=comment_for_rotation_counting, content = result)

    else:
        result = ""
        result +="""
            <script>
                alert("먼저 로그인 하세요.")
            </script>
        """
        return render_template('/sign_in.html', alert = result)

# 댓글 수정 버튼 누르면 넘어 오는 라우트 함수
@app.route('/community/amend_com', methods =['GET'])
def amend_com():
    if 'id' in session:
        c_number = request.args.get('c_number')
        id = session['id']

        sql="""
            SELECT c.MEMBER_ID from LIBRARY.COMMENT as c 
            where c.COMMENT_NUMBER = '{}';
            """.format(c_number)
        conn=get_conn()
        cur=conn.cursor()
        cur.execute(sql)

        for id_test in cur:
            continue
        if id_test[0] == id:

            sql= """
                SELECT COMMENT, MEMBER_ID, COMMENT_NUMBER from LIBRARY.COMMENT
                where COMMENT_NUMBER = {};
                """.format(c_number)
            conn=get_conn()
            cur=conn.cursor()
            cur.execute(sql)
            result = ""

            for (comment, c_id, c_number) in cur:
                result += """
                    <form action='/community/write_com' method="POST">
                        <p>작성자 : {1}</p><br>
                        <p>수정할 댓글 내용</p><br>
                        <textarea style="width: 100%; resize: none;" name="amend_com">{0}</textarea><br>
                        <input type="hidden" name="amend_c_number" value="{2}"><br>
                        <input type="submit" style="float:right; " value="저장" onclick=""><br>
                    </form>
                    """.format(comment, c_id, c_number)
                # amend_com.html로 넘어가서 변경 내용을 작성, 저장하면 /community/write_com로 넘어감.
            return render_template('/community/amend_com.html', content=result)

        else:

            alert = """
                    <script>
                        alert("수정권한이 없습니다.") 
                    </script>
                    """

            sql = """
                    SELECT c.POST_NUMBER from LIBRARY.COMMENT as c 
                    where c.COMMENT_NUMBER = {};
                """.format(c_number)

            conn = get_conn()
            cur = conn.cursor()
            cur.execute(sql)

            i = ()

            for i in cur:
                continue

            p_number = i[0]

            sql = """
                    SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                    from LIBRARY.COMMENT 
                    where POST_NUMBER = {};
                """.format(p_number)

            cur = conn.cursor()
            cur.execute(sql)

            comment_result = ""
            comment_for_rotation_counting = 0
            for (comment, id, date, c_modify_date, c_number) in cur:
                comment_for_rotation_counting += 1
                comment_result += """
                                <div class="container">
                                    <p>{0}</p>
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                    <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                    <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                </div>
                                <script>
                                    function com_delete_check_btn_{4}(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_com?del_c_number={4}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                            """.format(comment, id, date, c_modify_date, c_number)
            sql = """
                   SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                   p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                   left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                   WHERE p.NUMBER = {};
                   """.format(p_number)

            cur = conn.cursor()
            cur.execute(sql)

            i = []
            for i in cur:
                continue

            if bool(i[2]) == True:
                sql = """
                       SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                       p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                       left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                       WHERE p.NUMBER = {};
                       """.format(p_number)

                cur = conn.cursor()
                cur.execute(sql)

                for (title, contents, file, id, date, modify_date, p_number) in cur:
                    if modify_date == None:
                        modify_date = "None"
                        result = ''
                        result += """
                                <h3>{0}</h3>
                                <div class="container">
                                    <p>{1}</p>
                                    <div>
                                        <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                        <p class="h_sort">{7}</p>
                                    </div>                                 
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                    <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                </div>
                                <script>
                                    function delete_check_btn(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_doc?p_number={6}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                                """.format(title, contents, file, id, date, modify_date,
                                           p_number, os.path.basename(file))
                    else:
                        result = ''
                        result += """
                            <h3>{0}</h3>
                            <div class="container">
                                <p>{1}</p>
                                <div>
                                    <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                    <p class="h_sort">{7}</p>
                                </div>                                
                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                            </div>
                            <script>
                                function delete_check_btn(){{
                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                    window.location = '/community/delete_doc?p_number={6}';
                                  }} else{{
                                    return false;
                                  }}
                               }}
                            </script>
                            """.format(title, contents, file, id, date, modify_date, p_number,
                                       os.path.basename(file))
            else:
                sql = """
                    SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                    p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                    left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                    WHERE p.NUMBER = {};
                    """.format(p_number)

                cur = conn.cursor()
                cur.execute(sql)

                for (title, contents, file, id, date, modify_date, p_number) in cur:
                    if modify_date == None:
                        modify_date = "None"
                        result = ''
                        result += """
                            <h3>{0}</h3>
                            <div class="container">
                                <p>{1}</p>
                                <!-- <div>
                                      <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                      <p class="h_sort">{7}</p>
                                  </div>                                  -->                              
                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                            </div>
                            <script>
                                function delete_check_btn(){{
                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                    window.location = '/community/delete_doc?p_number={6}';
                                  }} else{{
                                    return false;
                                  }}
                               }}
                            </script>
                            """.format(title, contents, file, id, date, modify_date, p_number,
                                       "첨부파일 없음")
                    else:
                        result += """
                            <h3>{0}</h3>
                            <div class="container">
                                <p>{1}</p>
                                <!-- <div>
                                      <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                      <p class="h_sort">{7}</p>
                                  </div>                                  -->                               
                                <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                            </div>
                            <script>
                                function delete_check_btn(){{
                                  if(confirm("정말 삭제하시겠습니까?")==true){{
                                    window.location = '/community/delete_doc?p_number={6}';
                                  }} else{{
                                    return false;
                                  }}
                               }}
                            </script>
                            """.format(title, contents, file, id, date, modify_date, p_number,
                                       "첨부파일 없음")

            if conn:
                conn.close()
            return render_template('/community/watch_doc.html', com_content=comment_result, for_rotation_counting=comment_for_rotation_counting, content = result, alert = alert)


    else:
        alert = """
                    <script>
                        alert("로그인 후 이용하세요.")
                    </script>
                    """
        return render_template('/sign_in.html', alert=alert)

#댓글 삭제 버튼을 누르고 확인 버튼을 누르면 넘어오는 라우트 함수
@app.route('/community/delete_com', methods = ['GET'])
def delete_com():
    del_c_number = request.args.get("del_c_number")
    if 'id' in session:
        sql = """
            SELECT MEMBER_ID FROM LIBRARY.COMMENT
            where COMMENT_NUMBER ={};
            """.format(del_c_number)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        data = []
        for data in cur:
            continue
        if data[0] == session['id']:
            try:
                sql = """
                        SELECT POST_NUMBER from LIBRARY.COMMENT
                        where COMMENT_NUMBER = {}
                        """.format(del_c_number)

                conn = get_conn()
                cur = conn.cursor()
                cur.execute(sql)

                i = ()
                for i in cur:
                    continue
                p_number = i[0]

                sql = """
                    DELETE FROM LIBRARY.COMMENT
                    where COMMENT_NUMBER ={0};
                    """.format(del_c_number)

                cur=conn.cursor()
                cur.execute(sql)
                conn.commit()

                sql = """
                        SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                        from LIBRARY.COMMENT 
                        where POST_NUMBER = {};
                    """.format(p_number)

                cur = conn.cursor()
                cur.execute(sql)

                comment_result = ""
                comment_for_rotation_counting = 0
                for (comment, id, date, c_modify_date, c_number) in cur:
                    comment_for_rotation_counting += 1
                    comment_result += """
                                    <div class="container">
                                        <p>{0}</p>
                                        <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                        <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                        <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                    </div>
                                    <script>
                                        function com_delete_check_btn_{4}(){{
                                          if(confirm("정말 삭제하시겠습니까?")==true){{
                                            window.location = '/community/delete_com?del_c_number={4}';
                                          }} else{{
                                            return false;
                                          }}
                                       }}
                                    </script>
                                """.format(comment, id, date, c_modify_date, c_number)
                sql = """
                       SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                       p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                       left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                       WHERE p.NUMBER = {};
                       """.format(p_number)

                cur = conn.cursor()
                cur.execute(sql)

                i = []
                for i in cur:
                    continue

                if bool(i[2]) == True:
                    sql = """
                                       SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                                       p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                                       left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                                       WHERE p.NUMBER = {};
                                       """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    for (title, contents, file, id, date, modify_date, p_number) in cur:
                        if modify_date == None:
                            modify_date = "None"
                            result = ''
                            result += """
                                                <h3>{0}</h3>
                                                <div class="container">
                                                    <p>{1}</p>
                                                    <div>
                                                        <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                        <p class="h_sort">{7}</p>
                                                    </div>                                 
                                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                                    <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                                </div>
                                                <script>
                                                    function delete_check_btn(){{
                                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                                        window.location = '/community/delete_doc?p_number={6}';
                                                      }} else{{
                                                        return false;
                                                      }}
                                                   }}
                                                </script>
                                                """.format(title, contents, file, id, date, modify_date,
                                                           p_number, os.path.basename(file))
                        else:
                            result += """
                                                <h3>{0}</h3>
                                                <div class="container">
                                                    <p>{1}</p>
                                                    <div>
                                                        <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                        <p class="h_sort">{7}</p>
                                                    </div>                                
                                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                                    <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                                </div>
                                                <script>
                                                    function delete_check_btn(){{
                                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                                        window.location = '/community/delete_doc?p_number={6}';
                                                      }} else{{
                                                        return false;
                                                      }}
                                                   }}
                                                </script>
                                                """.format(title, contents, file, id, date, modify_date, p_number,
                                                           os.path.basename(file))
                else:
                    sql = """
                                        SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                                        p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                                        left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                                        WHERE p.NUMBER = {};
                                        """.format(p_number)

                    cur = conn.cursor()
                    cur.execute(sql)

                    for (title, contents, file, id, date, modify_date, p_number) in cur:
                        if modify_date == None:
                            modify_date = "None"
                            result = ''
                            result += """
                                                <h3>{0}</h3>
                                                <div class="container">
                                                    <p>{1}</p>
                                                    <!-- <div>
                                                          <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                          <p class="h_sort">{7}</p>
                                                      </div>                                  -->                             
                                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                                    <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                                </div>
                                                <script>
                                                    function delete_check_btn(){{
                                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                                        window.location = '/community/delete_doc?p_number={6}';
                                                      }} else{{
                                                        return false;
                                                      }}
                                                   }}
                                                </script>
                                                """.format(title, contents, file, id, date, modify_date, p_number,
                                                           "첨부파일 없음")
                        else:
                            result += """
                                                <h3>{0}</h3>
                                                <div class="container">
                                                    <p>{1}</p>
                                                    <!-- <div>
                                                          <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                                          <p class="h_sort">{7}</p>
                                                      </div>                                  -->                          
                                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                                    <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                                </div>
                                                <script>
                                                    function delete_check_btn(){{
                                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                                        window.location = '/community/delete_doc?p_number={6}';
                                                      }} else{{
                                                        return false;
                                                      }}
                                                   }}
                                                </script>
                                                """.format(title, contents, file, id, date, modify_date, p_number,
                                                           "첨부파일 없음")

                return render_template('/community/watch_doc.html', com_content=comment_result,
                                       for_rotation_counting=comment_for_rotation_counting, content=result)




            except mariadb.Error as e:
                print(e)
                sys.exit(1)
            except TypeError as e:
                print(e)
            if conn:
                conn.close()

            return render_template('/main.html')

        #로그인한 사용자가 다른 회원의 댓글을 삭제하려는 경우
        else:
            alert = """
                        <script>
                            alert("삭제 권한이 없습니다.")
                        </script>
                    """
            sql = """
                SELECT POST_NUMBER from LIBRARY.COMMENT
                where COMMENT_NUMBER = {}
                """.format(del_c_number)

            conn = get_conn()
            cur = conn.cursor()
            cur.execute(sql)

            i = ()
            for i in cur:
                continue
            p_number = i[0]

            sql = """
                    SELECT COMMENT, MEMBER_ID, DATE, MODIFY_DATE, COMMENT_NUMBER 
                    from LIBRARY.COMMENT 
                    where POST_NUMBER = {};
                """.format(p_number)

            cur = conn.cursor()
            cur.execute(sql)

            comment_result = ""
            comment_for_rotation_counting = 0
            for (comment, id, date, c_modify_date, c_number) in cur:
                comment_for_rotation_counting += 1
                comment_result += """
                                <div class="container">
                                    <p>{0}</p>
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : com_delete_check_btn_{4}()">
                                    <input class="float-right" type="button" value="수정" onclick = "location.href='/community/amend_com?c_number={4}'">
                                    <button class="float-right" disabled><span>작성자 : {1} 작성일시 : {2} 최종 수정일 : {3}</span></button> 
                                </div>
                                <script>
                                    function com_delete_check_btn_{4}(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_com?del_c_number={4}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                            """.format(comment, id, date, c_modify_date, c_number)
            sql = """
                   SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                   p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                   left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                   WHERE p.NUMBER = {};
                   """.format(p_number)

            cur = conn.cursor()
            cur.execute(sql)

            i = []
            for i in cur:
                continue

            if bool(i[2]) == True:
                sql = """
                       SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                       p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                       left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                       WHERE p.NUMBER = {};
                       """.format(p_number)

                cur = conn.cursor()
                cur.execute(sql)

                for (title, contents, file, id, date, modify_date, p_number) in cur:
                    if modify_date == None:
                        modify_date = "None"
                        result = ''
                        result += """
                                <h3>{0}</h3>
                                <div class="container">
                                    <p>{1}</p>
                                    <div>
                                        <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                        <p class="h_sort">{7}</p>
                                    </div>                                 
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                    <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                </div>
                                <script>
                                    function delete_check_btn(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_doc?p_number={6}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                                """.format(title, contents, file, id, date, modify_date,
                                           p_number, os.path.basename(file))
                    else:
                        result += """
                                <h3>{0}</h3>
                                <div class="container">
                                    <p>{1}</p>
                                    <div>
                                        <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                        <p class="h_sort">{7}</p>
                                    </div>                                
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                    <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                </div>
                                <script>
                                    function delete_check_btn(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_doc?p_number={6}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                                """.format(title, contents, file, id, date, modify_date, p_number,
                                           os.path.basename(file))
            else:
                sql = """
                        SELECT p.title, p.CONTENTS, p.post_file, m.id, p.date,
                        p.MODIFY_DATE, p.number FROM LIBRARY.POST as p
                        left join LIBRARY.MEMBER as m on p.MEMBER_NUMBER = m.NUMBER
                        WHERE p.NUMBER = {};
                        """.format(p_number)

                cur = conn.cursor()
                cur.execute(sql)

                for (title, contents, file, id, date, modify_date, p_number) in cur:
                    if modify_date == None:
                        modify_date = "None"
                        result = ''
                        result += """
                                <h3>{0}</h3>
                                <div class="container">
                                    <p>{1}</p>
                                    <!-- <div>
                                          <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                          <p class="h_sort">{7}</p>
                                      </div>                                  -->                             
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                    <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                </div>
                                <script>
                                    function delete_check_btn(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_doc?p_number={6}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                                """.format(title, contents, file, id, date, modify_date, p_number,
                                           "첨부파일 없음")
                    else:
                        result += """
                                <h3>{0}</h3>
                                <div class="container">
                                    <p>{1}</p>
                                    <!-- <div>
                                          <a class="h_sort" href ="{2}" download><input type="button" value="첨부파일 다운로드"></a>
                                          <p class="h_sort">{7}</p>
                                      </div>                                  -->                          
                                    <input class="float-right" type="button" value="삭제" onclick="javascript : delete_check_btn()">
                                    <input class="float-right" type="button" value="수정" onclick="location.href='/community/amend_doc?p_number={6}'">
                                    <button class="float-right" disabled><span style="color: white;">작성자 : {3} 작성일시 : {4} 최종 수정 : {5}</span></button>    
                                </div>
                                <script>
                                    function delete_check_btn(){{
                                      if(confirm("정말 삭제하시겠습니까?")==true){{
                                        window.location = '/community/delete_doc?p_number={6}';
                                      }} else{{
                                        return false;
                                      }}
                                   }}
                                </script>
                                """.format(title, contents, file, id, date, modify_date, p_number,
                                           "첨부파일 없음")

            return render_template('/community/watch_doc.html', com_content=comment_result, for_rotation_counting= comment_for_rotation_counting, content = result, alert=alert)

    else:
        alert = """
                <script>
                    alert("로그인되지 않았습니다. 먼저 회원가입 혹은 로그인을 하세요.")
                </script>
            """
        return render_template('/sign_in.html', alert=alert)

@app.route('/community/check_login')
def check_login():
    if 'id' in session: # session에 id 값이 있다면(로그인이 돼 있다면)
        author = session['id']
        return render_template("/community/write_doc.html", author = author)
    else:
        alert = """
            <script>
                alert("글을 작성하려면 회원가입 혹은 로그인을 하세요.")
            </script>
            """
        return render_template('/sign_in.html', alert = alert )

@app.route('/books')
def books():
    ##################################################################################
    #   2020-10-20 정원준                                                             #
    #   books 페이지 aside 카테고리 목록 및 책 목록 조회                                   #
    ###################################################################################

    # catagory_number - 좌측 C, Java 등의 책 카테고리의 DB의 number값
    # title - 책 제목 검색
    # session[number] - login 후 session에 보관하는 회원정보의 number 값(PK)
    catagory_number = request.args.get("catagory_number")
    title = request.args.get("title")

    if 'number' in session: number = session['number']
    else: number = ""

    try:
        ############################################################################################################
        # 책 카테고리 목록 조회 및 구성                                                                                #
        sql = "SELECT NUMBER, NAME FROM CATAGORY_BOOK ORDER BY NUMBER "

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)

        aside = """
            <li><h4><a href="/books">전체보기</a></h4></li>"""

        for (NUMBER, NAME) in cur:
            aside += """
            <li><a href="/books?catagory_number='{0}'">{1}</a></li>""".format(NUMBER, NAME)
        #                                                                                                          #
        ############################################################################################################

        ############################################################################################################
        # 책 목록 조회 및 구성                                                                                        #
        sql = """
        SELECT B.NUMBER, B.NAME, B.IMG, B.LOAN, R.MEMBER_NUMBER, B.CONTENTS FROM RENTER_RECORD R
        JOIN BOOK B
        ON B.NUMBER = R.BOOK_NUMBER 
        AND R.LOAN = 'N'"""

        sql2 = """
        UNION ALL
        SELECT B.NUMBER, B.NAME, B.IMG, B.LOAN ,0 AS MEMBER_NUMBER, B.CONTENTS FROM BOOK B 
        WHERE LOAN != 'N'
        """

        if catagory_number is not None:
            sql += "AND CATAGORY_NUMBER = "
            sql += catagory_number + " "
            sql2 += "AND CATAGORY_NUMBER = "
            sql2 += catagory_number + " "

        if title is not None:
            sql += "AND NAME LIKE '%{0}%' ".format(title)
            sql2 += "AND NAME LIKE '%{0}%' ".format(title)

        sql2 += """ORDER BY NUMBER ASC
        """

        sql += sql2
        cur = conn.cursor()
        cur.execute(sql)
        result = ""

        for (NUMBER, NAME, IMG, LOAN, MEMBER_NUMBER, CONTENTS) in cur:
            result += """
                    <div class="book" id="book_{0}">
                        <input type="image" src="{2}" alt="책" width="100px" height="160px" onclick="book_datails(this,'{0}')">
                        <span id="book_text_{0}" style="display:none">{3}</span>
                        <span id="book_name_{0}">{1}</span>""".format(NUMBER, NAME, IMG, CONTENTS)
            if MEMBER_NUMBER == number:
                if LOAN != 'Y':
                    result += """
                        <button class="click_button" type="button" id="book_borrow_{0}" onclick="return_book('{0}',this)">반납</button>
                    </div>""".format(NUMBER)
            else:
                if LOAN == 'Y':
                    if number == "":
                        result += """
                        <button class="click_button" type="button" id="book_borrow_{0}" onclick="login_alert()">대여</button>
                    </div>""".format(NUMBER)
                    else:
                        result += """
                        <button class="click_button" type="button" id="book_borrow_{0}" onclick="borrow_book('{0}',this)">대여</button>
                    </div>""".format(NUMBER)
                else:
                    result += """
                        <span id="book_borrow_{0}">대여 중</span>
                    </div>""".format(NUMBER)

    except mariadb.Error as e:
        print(e)
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return render_template("/books.html", tag=aside, content=result)

@app.route('/book_borrow')
def book_borrow():
    ##################################################################################
    #   2020-10-20 정원준                                                             #
    #   책 대여 ajax 기능                                                              #
    ###################################################################################

    # session["id"] - login 후 session에 보관하는 회원정보의 id 값
    # request.args.get("book_number") - 대여처리 해야하는 book의 테이블 number 값(PK)
    id = session["id"]
    book_number = request.args.get("book_number")

    try:
        ####################################################################################
        # 대여기록 테이블에 대여기록 INSERT
        sql = "INSERT INTO RENTER_RECORD (MEMBER_NUMBER, BOOK_NUMBER, DATE, RETURN_DATE, LOAN) VALUES((SELECT NUMBER FROM MEMBER WHERE ID='{0}'), {1}, NOW(), NULL, 'N')".format(id, book_number)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        ####################################################################################

        ####################################################################################
        # 책 테이블에 대여여부 컬럼 UPDATE
        sql = "UPDATE BOOK SET LOAN = 'N' WHERE NUMBER = {0}".format(book_number)

        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

    except mariadb.Error as e:
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return "대여 성공!"

@app.route('/book_return')
def return_book():
    ##################################################################################
    #   2020-10-20 정원준                                                             #
    #   책 반납 ajax 기능                                                              #
    ###################################################################################

    # session["id"] - login 후 session에 보관하는 회원정보의 id 값
    # session["number"] - login 후 session에 보관하는 회원정보의 number 값
    # request.args.get("book_number") - 대여처리 해야하는 book의 테이블 number 값(PK)
    id = session["id"]
    number = session["number"]
    book_number = request.args.get("book_number")

    try:
        ####################################################################################
        # 대여기록 테이블에 대여기록 (반납시간 = NULL -> 현재 연월일, 반납여부 = N -> Y ) UPDATE
        sql = "UPDATE BOOK SET LOAN = 'Y' WHERE NUMBER = {0}".format(book_number)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

        sql = "UPDATE RENTER_RECORD SET LOAN = 'Y', RETURN_DATE = NOW() WHERE MEMBER_NUMBER = {0} AND BOOK_NUMBER = {1} ".format(number, book_number)

        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        ####################################################################################

    except mariadb.Error as e:
        result = "사용자 없음."
        sys.exit(1)
    except TypeError as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return "반납 성공!!"


class remeber_p_number():

    def __init__(self):
        self.post_number_cl = ''

    def insert_p_number(self,number):
        self.post_number_cl = number

    def return_p_number(self):
        return self.post_number_cl


if __name__ == "__main__":
    check_p_number = remeber_p_number()
    app.secret_key = 'app secret key'
    app.run(host='0.0.0.0')







