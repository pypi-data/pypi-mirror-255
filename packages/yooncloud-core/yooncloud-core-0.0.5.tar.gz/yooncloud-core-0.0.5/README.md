# How to Deploy
<pre><code>
# src 를 제외한 모든 디렉토리 삭제한뒤
python setup.py sdist bdist_wheel
python3 -m twine upload dist/*
</code></pre>

<br>

이후 나오는 터미널에 다음과같이 입력. pypi 에서 발급받은 토큰을 복붙 해야한다.

<pre>
$ Enter your username: __token__
$ Enter your password: <여기에 pypi 토큰 복붙>
</pre>

