from .base import *


# MultiProcess
def multiprocess_items(funcion, items:int, worker:list, display=False):
    r"""list() 데이터를  function 에 multiprocessing 반복적용
    function : 반복적용할 함수
    items    : function 에 입력할 데이터"""

    with Pool(worker) as pool:
        if display:
            items = list(tqdm(pool.imap(funcion, items), total=len(items)))
        else:
            items = pool.map(funcion, items)
        return items


# http://taewan.kim/tip/python_pickle/
def file_pickle(
        file_path:str=None,
        option='w', 
        data=None
    ):
    r"""파이썬 객체를 Pickle 로 저장하고 호출
    file (str) : 파일이름
    option (str) : w,r (Write / Read)
    data (any) : pickle 로 저장할 
    """

    assert option in ['w', 'r'], f"`option` 은 `w`,`r` 하나를 입력하세요."
    option = {'w':'wb', 'r':'rb'}[option]

    with open(file_path, option) as f:
        if option == 'wb':
            assert data is not None, f"{data} 값을 저장 할 수 없습니다."
            pickle.dump(data, f)
            print(f"{file_path} saving done.")
            return None

        elif option == 'rb':
            assert data is None, f"불러오는 경우, {data}는 필요 없습니다."
            return pickle.load(f)