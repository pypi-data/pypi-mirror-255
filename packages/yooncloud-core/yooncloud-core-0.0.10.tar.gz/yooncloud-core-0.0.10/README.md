# How to deploy
setup.py 의 버전명을 수정한뒤
<pre><code>python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*</code></pre>

.pypitoken 파일의 내용물인 pypi에서 미리 발급받은 토큰을 복붙한다.

<pre><code>$ Enter your username: __token__
$ Enter your password: <여기에 pypi 토큰 복붙>
</code></pre>