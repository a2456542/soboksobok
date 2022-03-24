import React, { useEffect, useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import MultipleSelectChips from '../MultipleSelectChips.js';
import getAxios from '../api.js';
import SidoSelectBox from './Filter/Sido.jsx';
import GugunSelectBox from './Filter/Gugun.jsx';

const map = new Map();
map.set(14, '15'); //서구
map.set(15, 0); //학생
map.set(16, 1); //무직
map.set(17, 2); //창업
map.set(18, 3); //농어업인
map.set(19, 4); //중소기업
map.set(20, 5); //일반
map.set(21, 1); //자녀 있
map.set(22, 2); //자녀 없
map.set(23, 0); //무주택자
map.set(24, 1); //임산부
map.set(25, 2); //미취학
map.set(26, 3); //다문화/탈북민
map.set(27, 4); //다자녀
map.set(28, 5); //보훈대상자
map.set(29, 6); //장애인
map.set(30, 7); //저소득
map.set(31, 8); //한부모/조손
map.set(32, 9); //신용불량자
map.set(33, 10); //독거노인
map.set(34, 11); //취약계층

function FilterChips() {
  const [value, setValue] = useState([]);
  const [error, setError] = useState('');
  const [isAll, setIsAll] = useState('All');

  const job = [
    { label: '학생', value: 15 },
    { label: '무직 (실업자(취업희망자))', value: 16 },
    { label: '창업(영세자영업(창업)자)', value: 17 },
    { label: '농어업인', value: 18 },
    { label: '중소기업(저소득근로자)', value: 19 },
    { label: '일반', value: 20 },
  ];
  const child = [
    { label: '있음(출산예정/ 입양예정)', value: 21 },
    { label: '없음', value: 22 },
  ];
  const family = [
    { label: '무주택자', value: 23 },
    { label: '임산부', value: 24 },
    { label: '미취학', value: 25 },
    { label: '다문화/탈북민', value: 26 },
    { label: '다자녀', value: 27 },
    { label: '보훈대상자', value: 28 },
    { label: '장애인', value: 29 },
    { label: '저소득', value: 30 },
    { label: '한부모/조손', value: 31 },
    { label: '신용불량자', value: 32 },
    { label: '독거노인', value: 33 },
    { label: '저취약계층소득', value: 34 },
  ];

  const selectRegion = [];
  const selectJob = [];
  const selectChild = [];
  const selectFamily = [];

  for (let element of value) {
    if (element >= 8 && element <= 14) {
      selectRegion.push(map.get(element));
    } else if (element >= 15 && element <= 20) {
      selectJob.push(map.get(element));
    } else if (element >= 21 && element <= 22) {
      selectChild.push(map.get(element));
    } else if (element >= 23 && element <= 34) {
      selectFamily.push(map.get(element));
    }
  }
  // console.log(
  //   'selectRegion: ' +
  //     selectRegion +
  //     'selectJob: ' +
  //     selectJob +
  //     ' selectChild: ' +
  //     selectChild +
  //     ' selectFamily: ' +
  //     selectFamily
  // );

  const setFilter = async () => {
    try {
      const axios = getAxios();
      console.log(axios.defaults.headers);
      console.log({
        child: selectChild,
        region: selectRegion,
        job: selectJob,
        family: selectFamily,
      });

      await axios.post('/api/users/update', {
        child: selectChild[0],
        region: selectRegion[0],
        job: selectJob,
        family: selectFamily,
      });
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div>
      <SidoSelectBox setIsAll={setIsAll} />
      <GugunSelectBox isAll={isAll} />
      {/* <SelectBox options={SIDO} defaultValue="시/도 선택"></SelectBox>
      <SelectBox2 options={GUGUN} defaultValue="시/도 선택"></SelectBox2> */}

      <MultipleSelectChips
        label="대상특성"
        value={value}
        setValue={setValue}
        options={job}
        error={error}
        setError={setError}
      />
      <MultipleSelectChips
        label="자녀유무"
        value={value}
        setValue={setValue}
        options={child}
        error={error}
        setError={setError}
      />
      <MultipleSelectChips
        label="가구특성"
        value={value}
        setValue={setValue}
        options={family}
        error={error}
        setError={setError}
      />
      <Button
        variant="primary"
        onClick={() => {
          setFilter();
          // navigate('/', { replace: true });
        }}
      >
        저장
      </Button>
    </div>
  );
}

export default FilterChips;
