const JOB_REFERENCE_ITEMS = [
    {
        id: 'hkust-teaching-building',
        category: 'Ceiling System',
        nameKey: 'hkustTeachingBuilding',
        descKey: 'hkustTeachingBuildingDescription',
        image: '/assets/job-references/hkust-teaching-building.png',
        locationKey: 'locationHKUST',
        properties: [
            ['productSpecs', 'hkustProductSpecs'],
            ['productSeries', 'hkustProductSeries'],
            ['applicationArea', 'hkustApplicationArea'],
            ['performanceFeatures', 'acousticSoundAbsorption']
        ],
        applications: ['university', 'educationalInstitution', 'acousticControl']
    },
    {
        id: 'central-music-hall',
        category: 'Ceiling System',
        nameKey: 'centralMusicHall',
        descKey: 'centralMusicHallDescription',
        image: '/assets/job-references/central-music-hall.png',
        locationKey: 'locationCentralMusicHall',
        properties: [
            ['systemType', 'Acoustic Panel'],
            ['panelSize', '1200x1200mm'],
            ['loadCapacity', '20 kg/m²'],
            ['lightReflectance', '90%']
        ],
        applications: ['concertHall', 'performanceSpace', 'acousticControl']
    },
    {
        id: 'chongqing-university',
        category: 'Ceiling System',
        nameKey: 'chongqingUniversity',
        descKey: 'chongqingUniversityDescription',
        image: '/assets/job-references/chongqing-university.png',
        locationKey: 'locationChongqingUniversity',
        properties: [
            ['wallArea', 'wallAreaValue'],
            ['wallPanelType', 'wallPanelTypeValue'],
            ['ceilingArea', 'ceilingAreaValue'],
            ['ceilingPanelType', 'ceilingPanelTypeValue'],
            ['reverberationTime', 'reverberationBefore'],
            ['speechTransmission', 'speechTransmissionBefore']
        ],
        applications: ['auditorium', 'educationalInstitution', 'acousticControl']
    },
    {
        id: 'kazakhstan-ballroom-academy',
        category: 'Ceiling System',
        nameKey: 'kazakhstanBallroomAcademy',
        descKey: 'kazakhstanBallroomAcademyDescription',
        image: '/assets/job-references/kazakhstan-ballroom-academy.png',
        locationKey: 'locationKazakhstanBallroomAcademy',
        properties: [
            ['productSpecs', 'kazakhstanProductSpecs'],
            ['productSeries', 'kazakhstanProductSeries'],
            ['applicationArea', 'kazakhstanApplicationArea'],
            ['performanceFeatures', 'acousticSoundAbsorption']
        ],
        applications: ['ballroomDance', 'performanceSpace', 'acousticControl']
    },
    {
        id: 'seoul-metro-line-9',
        category: 'Ceiling System',
        nameKey: 'seoulMetroLine9',
        descKey: 'seoulMetroLine9Description',
        image: '/assets/job-references/seoul-metro-line-9.png',
        locationKey: 'locationSeoulMetroLine9',
        properties: [
            ['applicationArea', 'publicArea'],
            ['productUsed', 'beiyangYashangSeries'],
            ['suspensionSystem', 'hardConnectionSystem'],
            ['performanceFeatures', 'stabilityWindEarthquake']
        ],
        applications: ['metroStation', 'publicTransport', 'acousticControl']
    },
    {
        id: 'beijing-lenovo-headquarters',
        category: 'Ceiling System',
        nameKey: 'beijingLenovoHQ',
        descKey: 'beijingLenovoHQDescription',
        image: '/assets/job-references/beijing-lenovo-headquarters.png',
        locationKey: 'locationBeijingLenovoHQ',
        properties: [
            ['applicationArea', 'officeActivityCenter'],
            ['productUsed', 'beiyangYashangWaterFlat'],
            ['designFeature', 'variousShapesColors'],
            ['acousticBenefit', 'noiseReductionClarity']
        ],
        applications: ['corporateOffice', 'businessFacility', 'acousticControl']
    },
    {
        id: 'shenzhen-luohu-hospital',
        category: 'Ceiling System',
        nameKey: 'shenzhenLuohuHospital',
        descKey: 'shenzhenLuohuHospitalDescription',
        image: '/assets/job-references/shenzhen-luohu-hospital.png',
        locationKey: 'locationShenzhenLuohuHospital',
        properties: [
            ['applicationArea', 'inpatientCorridorClinic'],
            ['productUsed', 'beiyangTuoshiOpenCeiling'],
            ['acousticBenefit', 'soundPressureReduction'],
            ['performanceFeatures', 'lightweightEasyMaintenance']
        ],
        applications: ['hospital', 'healthcareFacility', 'acousticControl']
    },
    {
        id: 'china-chemical-engineering',
        category: 'Ceiling System',
        nameKey: 'chinaChemicalEngineering',
        descKey: 'chinaChemicalEngineeringDescription',
        image: '/assets/job-references/china-chemical-engineering.png',
        locationKey: 'locationChinaChemicalEngineering',
        properties: [
            ['applicationArea', 'badmintonStadium'],
            ['productUsed', 'beiyangYashangWaterFlatSeries'],
            ['designFeature', 'elegantSuspensionInstallation'],
            ['acousticBenefit', 'backgroundNoiseReduction']
        ],
        applications: ['sportsFacility', 'badmintonHall', 'acousticControl']
    },
    {
        id: 'de-montfort-university-office-building',
        category: 'Ceiling System',
        nameKey: 'deMontfortUniversity',
        descKey: 'deMontfortUniversityDescription',
        image: '/assets/job-references/de-montfort-university-office-building.png',
        locationKey: 'locationDeMontfortUniversity',
        properties: [
            ['applicationArea', 'library'],
            ['productUsed', 'beiyangYashangWaterFlatSeries'],
            ['designFeature', 'elegantSuspensionInstallation'],
            ['acousticBenefit', 'backgroundNoiseReduction']
        ],
        applications: ['educationalInstitution', 'library', 'acousticControl']
    },
    {
        id: 'pudong-international-airport',
        category: 'Raised Floor System',
        nameKey: 'pudongAirport',
        descKey: 'pudongAirportDescription',
        image: '/assets/job-references/pudong-international-airport.png',
        locationKey: 'locationPudongAirport',
        properties: [
            ['floorType', 'Steel raised floor'],
            ['projectQuantity', 'pudongQuantity'],
            ['floorApplication', 'airportTerminal'],
            ['performanceFeatures', 'highLoadStructural']
        ],
        applications: ['airport', 'transportHub', 'structuralSupport']
    },
    {
        id: 'shenzhen-hnbc-headquarter',
        category: 'Raised Floor System',
        nameKey: 'shenzhenHnbc',
        descKey: 'shenzhenHnbcDescription',
        image: '/assets/job-references/shenzhen-hnbc-headquarter.png',
        locationKey: 'locationShenzhenHnbc',
        properties: [
            ['floorType', 'Steel raised floor'],
            ['projectQuantity', 'hnbcQuantity'],
            ['floorApplication', 'corporateHeadquarter'],
            ['performanceFeatures', 'highLoadStructural']
        ],
        applications: ['commercialBuilding', 'officeSpace', 'structuralSupport']
    },
    {
        id: 'macau-studio-city',
        category: 'Raised Floor System',
        nameKey: 'macauStudioCity',
        descKey: 'macauStudioCityDescription',
        image: '/assets/job-references/macau-studio-city.png',
        locationKey: 'locationMacauStudioCity',
        properties: [
            ['productUsed', 'macauProduct'],
            ['projectQuantity', 'macauQuantity'],
            ['floorApplication', 'entertainmentVenue'],
            ['performanceFeatures', 'highLoadStructural']
        ],
        applications: ['entertainmentComplex', 'studioSpace', 'structuralSupport']
    },
    {
        id: 'macau-galaxy-3a-gaming-area',
        category: 'Raised Floor System',
        nameKey: 'macauGalaxy3A',
        descKey: 'macauGalaxy3ADescription',
        image: '/assets/job-references/macau-galaxy-3a-gaming-area.png',
        locationKey: 'locationMacauGalaxy3A',
        properties: [
            ['productUsed', 'macauGalaxy3AProduct'],
            ['projectQuantity', 'macauGalaxy3AQuantity'],
            ['supplyDate', 'macauGalaxy3ASupplyDate'],
            ['floorApplication', 'gamingArea']
        ],
        applications: ['entertainmentComplex', 'casino', 'gamingFacility']
    },
    {
        id: 'mgm-cotai',
        category: 'Raised Floor System',
        nameKey: 'mgmCotai',
        descKey: 'mgmCotaiDescription',
        image: '/assets/job-references/mgm-cotai.png',
        locationKey: 'locationMgmCotai',
        properties: [
            ['productUsed', 'mgmCotaiProduct'],
            ['projectQuantity', 'mgmCotaiQuantity'],
            ['floorApplication', 'integratedResort'],
            ['performanceFeatures', 'highLoadStructural']
        ],
        applications: ['entertainmentComplex', 'casino', 'resortFacility']
    }
];

const JOB_REFERENCE_STRINGS = {
    EN: {
        centralMusicHall: 'Central Music Hall',
        centralMusicHallDescription: 'A high-end ceiling system designed for concert halls and performance spaces, offering exceptional acoustic performance and aesthetic appeal.',
        hkustTeachingBuilding: 'Hong Kong University of Science and Technology Teaching Building',
        hkustTeachingBuildingDescription: 'A state-of-the-art ceiling system installed in the HKUST teaching building, featuring Tuoshi Yingji series panels. Designed specifically for educational environments, providing excellent acoustic control and aesthetic appeal in corridors and learning spaces.',
        chongqingUniversity: 'Chongqing University',
        chongqingUniversityDescription: 'Auditorium (Report Hall) acoustic renovation project with professional wall and ceiling acoustic treatment systems.',
        seoulMetroLine9: 'Korea Seoul Metro Line 9 Station',
        seoulMetroLine9Description: 'Uses Beiyang Yashang series fiberglass vertical hanging panels throughout public areas, significantly reducing reverberation time and effectively controlling background noise. Features specially developed hard connection suspension system for metro systems, ensuring stability, wind resistance, earthquake resistance, and durability.',
        beijingLenovoHQ: 'Beijing Lenovo Headquarters Building',
        beijingLenovoHQDescription: 'Top uses Beiyang Yashang water-flat hanging panel series products with various shapes, colors, and combinations, creating a lively and relaxed office atmosphere. Effectively reduces noise in office spaces and activity centers during busy times, improving indoor speech clarity and promoting higher quality communication.',
        shenzhenLuohuHospital: 'Shenzhen Luohu Chinese Medicine Hospital',
        shenzhenLuohuHospitalDescription: 'Uses Beiyang Tuoshi open ceiling series products throughout the top area. After installation, sound pressure level is significantly reduced, greatly improving recovery efficiency for hospitalized patients. Open ceiling system features lightweight material, easy installation, and convenient maintenance.',
        chinaChemicalEngineering: 'China Chemical Engineering Third Construction Co., Ltd.',
        chinaChemicalEngineeringDescription: 'Indoor ceiling uses high-quality glass fiber absorption products, with elegant suspension installation and high-quality large-area conversion effects, creating simple and fashionable ceiling spaces. Features excellent appearance while significantly reducing indoor background noise and improving reverberation time.',
        kazakhstanBallroomAcademy: 'Kazakhstan International Ballroom Dance Academy',
        kazakhstanBallroomAcademyDescription: 'A specialized ceiling system designed for ballroom dance academy featuring Accord vertical hanging panel series. The system provides excellent acoustic control and aesthetic appeal, creating an optimal environment for dance performances and training.',
        deMontfortUniversity: 'De Montfort University Office Building',
        deMontfortUniversityDescription: 'A modern university office building featuring an advanced ceiling system with Yashang series products. The open ceiling design creates a spacious and contemporary workspace while maintaining excellent acoustic performance and visual appeal.',
        systemType: 'System Type',
        panelSize: 'Panel Size',
        loadCapacity: 'Load Capacity',
        lightReflectance: 'Light Reflectance',
        wallArea: 'Wall Area',
        wallAreaValue: '60m²',
        wallPanelType: 'Wall Panel Type',
        wallPanelTypeValue: 'Beiyang Heyue Series 25mm Acoustic Panel',
        ceilingArea: 'Ceiling Area',
        ceilingAreaValue: '256m²',
        ceilingPanelType: 'Ceiling Panel Type',
        ceilingPanelTypeValue: 'Beiyang Yashang Series 50mm Vertical Hanging Panel System (Grid Pattern)',
        reverberationTime: 'Reverberation Time (Mid-frequency)',
        reverberationBefore: '2.48s → 0.7s',
        speechTransmission: 'Speech Transmission Index',
        speechTransmissionBefore: '0.43 (Poor) → 0.73 (Good)',
        applicationArea: 'Application Area',
        publicArea: 'Public Area',
        productUsed: 'Product Used',
        beiyangYashangSeries: 'Beiyang Yashang Vertical Hanging Panel Series',
        suspensionSystem: 'Suspension System',
        hardConnectionSystem: 'Hard Connection Suspension System',
        performanceFeatures: 'Performance Features',
        stabilityWindEarthquake: 'Stability, Wind & Earthquake Resistance, Durability',
        designFeature: 'Design Feature',
        variousShapesColors: 'Various Shapes & Colors',
        beiyangYashangWaterFlat: 'Beiyang Yashang Water-Flat Hanging Panel Series',
        acousticBenefit: 'Acoustic Benefit',
        noiseReductionClarity: 'Noise Reduction & Improved Speech Clarity',
        officeActivityCenter: 'Office Activity Center & Office',
        beiyangTuoshiOpenCeiling: 'Beiyang Tuoshi Open Ceiling Series',
        soundPressureReduction: 'Sound Pressure Level Reduction',
        lightweightEasyMaintenance: 'Lightweight, Easy Installation & Maintenance',
        inpatientCorridorClinic: 'Inpatient Ward Corridors, Outpatient Clinic',
        badmintonStadium: 'Badminton Stadium',
        beiyangYashangWaterFlatSeries: 'Beiyang Yashang Water-Flat Hanging Panel Series',
        elegantSuspensionInstallation: 'Elegant Suspension Installation',
        backgroundNoiseReduction: 'Background Noise Reduction & Reverberation Improvement',
        productSpecs: 'Product Specifications',
        kazakhstanProductSpecs: '600×2400×200mm',
        productSeries: 'Product Series',
        kazakhstanProductSeries: 'Accord - Vertical Hanging Panel Series',
        kazakhstanApplicationArea: 'Ballroom Dance Hall',
        acousticSoundAbsorption: 'Acoustic Sound Absorption & Reverberation Control',
        hkustProductSpecs: '600×1500×20mm',
        hkustProductSeries: 'Tuoshi - Yingji Series',
        hkustApplicationArea: 'Teaching Building Corridor',
        concertHall: 'Concert Hall',
        performanceSpace: 'Performance Space',
        acousticControl: 'Acoustic Control',
        university: 'University',
        educationalInstitution: 'Educational Institution',
        hospital: 'Hospital',
        healthcareFacility: 'Healthcare Facility',
        corporateOffice: 'Corporate Office',
        businessFacility: 'Business Facility',
        auditorium: 'Auditorium',
        metroStation: 'Metro Station',
        publicTransport: 'Public Transport',
        sportsFacility: 'Sports Facility',
        badmintonHall: 'Badminton Hall',
        ballroomDance: 'Ballroom Dance Academy',
        locationCentralMusicHall: 'Poland',
        locationChongqingUniversity: 'Chongqing, China',
        locationSeoulMetroLine9: 'Seoul, Korea',
        locationBeijingLenovoHQ: 'Beijing, China',
        locationShenzhenLuohuHospital: 'Shenzhen, China',
        locationChinaChemicalEngineering: 'Shenzhen, China',
        locationKazakhstanBallroomAcademy: 'Almaty, Kazakhstan',
        locationHKUST: 'Hong Kong',
        locationDeMontfortUniversity: 'Leicester, United Kingdom',
        library: 'Library',
        pudongAirport: 'Pudong International Airport',
        pudongAirportDescription: 'Steel raised floor system installed at Pudong International Airport with total area of 5600m². High-performance raised floor system designed for high-traffic airport environments.',
        shenzhenHnbc: 'Shenzhen HNBC Headquarter',
        shenzhenHnbcDescription: 'Steel raised floor system installed at Shenzhen HNBC Headquarter with total area of 40000m². Large-scale commercial installation providing superior structural support.',
        macauStudioCity: 'Macau Studio City',
        macauStudioCityDescription: 'PARETE steel raised floor (FS2000) system installed at Macau Studio City entertainment complex with total area of 12000m². Premium raised floor system designed for entertainment venues.',
        macauGalaxy3A: 'Macau Galaxy 3A Gaming Area',
        macauGalaxy3ADescription: 'PARETE steel raised floor FS2000 system installed at Macau Galaxy 3A Gaming Area with total area of 2200m². Premium raised floor system designed specifically for gaming and entertainment facilities, supplied in October 2021.',
        mgmCotai: 'MGM Cotai',
        mgmCotaiDescription: 'PARETE steel raised floor (FS1250) system installed at MGM Cotai integrated resort with total area of 650m². High-performance raised floor system designed for luxury hospitality and gaming facilities.',
        floorType: 'Floor Type',
        projectQuantity: 'Project Quantity',
        floorApplication: 'Floor Application',
        pudongQuantity: '5600 m²',
        hnbcQuantity: '40000 m²',
        macauQuantity: '12000 m²',
        macauProduct: 'PARETE steel raised floor (FS2000)',
        macauGalaxy3AProduct: 'PARETE steel raised floor FS2000',
        macauGalaxy3AQuantity: '2200 m²',
        macauGalaxy3ASupplyDate: 'October 2021',
        mgmCotaiProduct: 'PARETE steel raised floor (FS1250)',
        mgmCotaiQuantity: '650 m²',
        airportTerminal: 'Airport Terminal',
        corporateHeadquarter: 'Corporate Headquarter',
        entertainmentVenue: 'Entertainment Venue',
        gamingArea: 'Gaming Area',
        integratedResort: 'Integrated Resort',
        highLoadStructural: 'High Load Capacity & Structural Support',
        supplyDate: 'Supply Date',
        airport: 'Airport',
        transportHub: 'Transport Hub',
        structuralSupport: 'Structural Support',
        commercialBuilding: 'Commercial Building',
        officeSpace: 'Office Space',
        entertainmentComplex: 'Entertainment Complex',
        studioSpace: 'Studio Space',
        casino: 'Casino',
        gamingFacility: 'Gaming Facility',
        resortFacility: 'Resort Facility',
        locationPudongAirport: 'Shanghai, China',
        locationShenzhenHnbc: 'Shenzhen, China',
        locationMacauStudioCity: 'Macau',
        locationMacauGalaxy3A: 'Macau',
        locationMgmCotai: 'Macau'
    },
    '繁': {
        centralMusicHall: '中央音樂廳',
        centralMusicHallDescription: '為音樂廳和表演空間設計的高端天花板系統，提供卓越的聲學性能和美學吸引力。',
        hkustTeachingBuilding: '香港科技大學教學大樓',
        hkustTeachingBuildingDescription: '香港科技大學教學大樓安裝的先進天花板系統，採用圖時應機系列面板。專為教育環境設計，提供優秀的聲學控制和美學吸引力，適用於走廊和學習空間。',
        chongqingUniversity: '重慶大學',
        chongqingUniversityDescription: '報告廳聲學改造項目，配有專業的牆面和天花板聲學處理系統。',
        seoulMetroLine9: '韓國首爾地鐵9號線車站',
        seoulMetroLine9Description: '公共區域使用北洋雅尚系列纖維增強玻璃垂直吊掛面板，顯著減少混響時間並有效控制背景噪音。特為地鐵系統開發的硬連接懸掛系統，確保穩定性、抗風性、抗震性和耐久性。',
        beijingLenovoHQ: '北京聯想總部大樓',
        beijingLenovoHQDescription: '頂層使用北洋雅尚水平吊掛面板系列產品，具有各種形狀、顏色和組合，創造活躍而放鬆的辦公大氣氛。有效減少繁忙時辦公空間和活動中心的噪音，提高室內語音清晰度，促進更高質量的溝通。',
        shenzhenLuohuHospital: '深圳羅湖中醫醫院',
        shenzhenLuohuHospitalDescription: '全院頂部區域使用北洋圖時開放天花板系列產品。安裝後，聲壓級顯著降低，大幅提高住院患者的恢復效率。開放天花板系特點為輕質材料、安裝方便和維護便捷。',
        chinaChemicalEngineering: '中國化工第三建設有限公司',
        chinaChemicalEngineeringDescription: '室內天花板使用高品質玻璃纖維吸音產品，採用優雅懸掛安裝和高品質大面積轉換效果，創造簡單時尚的天花板空間。特點為外觀優美，顯著減少室內背景噪音並改善混響時間。',
        kazakhstanBallroomAcademy: '哈薩克斯坦國際芭蕾舞學院',
        kazakhstanBallroomAcademyDescription: '專為芭蕾舞學院設計的天花板系統，採用Accord垂直吊掛面板系列。該系統提供卓越的聲學控制和美學吸引力，創造出適合舞蹈表演和訓練的理想環境。',
        deMontfortUniversity: '德蒙福特大學辦公大樓',
        deMontfortUniversityDescription: '現代大學辦公大樓採用先進天花板系統，使用Yashang系列產品。開放天花板設計創造出寬敞現代的工作空間，同時保持卓越的聲學性能和視覺吸引力。',
        systemType: '系統類型',
        panelSize: '面板尺寸',
        loadCapacity: '負載能力',
        lightReflectance: '光反射率',
        wallArea: '牆面面積',
        wallAreaValue: '60m²',
        wallPanelType: '牆面面板類型',
        wallPanelTypeValue: '北洋合越系列 25mm 声学面板',
        ceilingArea: '天花板面積',
        ceilingAreaValue: '256m²',
        ceilingPanelType: '天花板面板類型',
        ceilingPanelTypeValue: '北洋雅尚系列 50mm 垂直吊挂面板系統 (網格圖案)',
        reverberationTime: '混響時間 (中頻)',
        reverberationBefore: '2.48s → 0.7s',
        speechTransmission: '語音傳輸指數',
        speechTransmissionBefore: '0.43 (差) → 0.73 (好)',
        applicationArea: '應用區域',
        publicArea: '公共區域',
        productUsed: '使用的產品',
        beiyangYashangSeries: '北洋雅尚垂直吊掛面板系列',
        suspensionSystem: '懸掛系統',
        hardConnectionSystem: '硬連接懸掛系統',
        performanceFeatures: '性能特點',
        stabilityWindEarthquake: '穩定性、抗風性、抗震性和耐久性',
        designFeature: '設計特點',
        variousShapesColors: '各種形狀和顏色',
        beiyangYashangWaterFlat: '北洋雅尚水平吊掛面板系列',
        acousticBenefit: '聲學效益',
        noiseReductionClarity: '降低噪音和提高語音清晰度',
        officeActivityCenter: '辦公活動中心和辦公室',
        beiyangTuoshiOpenCeiling: '北洋圖時開放天花板系列',
        soundPressureReduction: '聲壓級降低',
        lightweightEasyMaintenance: '輕質材料、安裝方便和維護便捷',
        inpatientCorridorClinic: '住院病房走廊、門診診所',
        badmintonStadium: '羽毛球場',
        beiyangYashangWaterFlatSeries: '北洋雅尚水平吊掛面板系列',
        elegantSuspensionInstallation: '優雅懸掛安裝',
        backgroundNoiseReduction: '降低背景噪音和改善混響時間',
        productSpecs: '產品規格',
        kazakhstanProductSpecs: '600×2400×200mm',
        productSeries: '產品系列',
        kazakhstanProductSeries: 'Accord - 垂直吊掛面板系列',
        kazakhstanApplicationArea: '芭蕾舞廳',
        acousticSoundAbsorption: '聲學吸音和混響控制',
        hkustProductSpecs: '600×1500×20mm',
        hkustProductSeries: 'Tuoshi - Yingji Series',
        hkustApplicationArea: '教學大樓走廊',
        concertHall: '樂廳',
        performanceSpace: '表演空間',
        acousticControl: '聲學控制',
        university: '大學',
        educationalInstitution: '教育機構',
        hospital: '醫院',
        healthcareFacility: '醫療設施',
        corporateOffice: '企業辦公室',
        businessFacility: '商業設施',
        auditorium: '禮堂',
        metroStation: '地鐵站',
        publicTransport: '公共交通',
        sportsFacility: '體育設施',
        badmintonHall: '羽毛球場',
        ballroomDance: '芭蕾舞學院',
        locationCentralMusicHall: '波蘭',
        locationChongqingUniversity: '重慶, 中國',
        locationSeoulMetroLine9: '首爾, 韓國',
        locationBeijingLenovoHQ: '北京, 中國',
        locationShenzhenLuohuHospital: '深圳, 中國',
        locationChinaChemicalEngineering: '深圳, 中國',
        locationKazakhstanBallroomAcademy: '阿拉木圖, 哈薩克斯坦',
        locationHKUST: '香港',
        locationDeMontfortUniversity: '萊斯特, 英國',
        library: '圖書館',
        pudongAirport: '浦東國際機場',
        pudongAirportDescription: '浦東國際機場安裝鋼製架空地板系統，總面積為5600m²。高性能架空地板系統設計用於高流量機場環境。',
        shenzhenHnbc: '深圳HNBC總部',
        shenzhenHnbcDescription: '深圳HNBC總部安裝鋼製架空地板系統，總面積為40000m²。大型商業安裝提供優秀的結構支持。',
        macauStudioCity: '澳門工作室城',
        macauStudioCityDescription: '澳門工作室城娛樂複合體安裝PARETE鋼製架空地板（FS2000）系統，總面積為12000m²。高端架空地板系統設計用於娛樂場所。',
        macauGalaxy3A: '澳門銀河3A遊戲區',
        macauGalaxy3ADescription: '澳門銀河3A遊戲區安裝PARETE鋼製架空地板FS2000系統，總面積為2200m²。高端架空地板系統專為遊戲和娛樂設施設計，於2021年10月供應。',
        mgmCotai: 'MGM Cotai',
        mgmCotaiDescription: 'MGM Cotai綜合度假村安裝PARETE鋼製架空地板（FS1250）系統，總面積為650m²。高性能架空地板系統設計用於豪華酒店和遊戲設施。',
        floorType: '地板類型',
        projectQuantity: '項目數量',
        floorApplication: '地板應用',
        pudongQuantity: '5600 m²',
        hnbcQuantity: '40000 m²',
        macauQuantity: '12000 m²',
        macauProduct: 'PARETE鋼製架空地板 (FS2000)',
        macauGalaxy3AProduct: 'PARETE鋼製架空地板 FS2000',
        macauGalaxy3AQuantity: '2200 m²',
        macauGalaxy3ASupplyDate: '2021年10月',
        mgmCotaiProduct: 'PARETE鋼製架空地板 (FS1250)',
        mgmCotaiQuantity: '650 m²',
        airportTerminal: '機場航站樓',
        corporateHeadquarter: '企業總部',
        entertainmentVenue: '娛樂場所',
        gamingArea: '遊戲區',
        integratedResort: '綜合度假村',
        highLoadStructural: '高負載能力及結構支持',
        supplyDate: '供應日期',
        airport: '機場',
        transportHub: '交通樞紐',
        structuralSupport: '結構支持',
        commercialBuilding: '商業建築',
        officeSpace: '辦公空間',
        entertainmentComplex: '娛樂複合體',
        studioSpace: '工作室空間',
        casino: '賭場',
        gamingFacility: '遊戲設施',
        resortFacility: '度假村設施',
        locationPudongAirport: '上海, 中國',
        locationShenzhenHnbc: '深圳, 中國',
        locationMacauStudioCity: '澳門',
        locationMacauGalaxy3A: '澳門',
        locationMgmCotai: '澳門'
    },
    '简': {
        centralMusicHall: '中央音乐厅',
        centralMusicHallDescription: '为音乐厅和表演空间设计的高端天花板系统，提供卓越的声学性能和美学吸引力。',
        hkustTeachingBuilding: '香港科技大学教学楼',
        hkustTeachingBuildingDescription: '香港科技大学教学楼安装的先进天花板系统，采用图时应机系列面板。专为教育环境设计，提供优秀的声学控制和美学吸引力，适用于走廊和学习空间。',
        chongqingUniversity: '重庆大学',
        chongqingUniversityDescription: '报告厅声学改造项目，配有专业的墙面和天花板声学处理系统。',
        seoulMetroLine9: '韩国首尔地铁9号线车站',
        seoulMetroLine9Description: '公共区域使用北洋雅尚系列纤维增强玻璃垂直吊挂面板，显著减少混响时间并有效控制背景噪音。特为地铁系统开发的硬连接悬挂系统，确保稳定性、抗风性、抗震性和耐久性。',
        beijingLenovoHQ: '北京联想总部大楼',
        beijingLenovoHQDescription: '顶层使用北洋雅尚水平吊挂面板系列产品，具有各种形状、颜色和组合，创造活跃而放松的办公氛围。有效减少繁忙时办公空间和活动中心的噪音，提高室内语音清晰度，促进更高质量的沟通。',
        shenzhenLuohuHospital: '深罗湖中医医院',
        shenzhenLuohuHospitalDescription: '全院顶部区域使用北洋图时开放天花板系列产品。安装后，声压级显著降低，大幅提高住院患者的恢复效率。开放天花板系统特点为轻质材料、安装方便和维护便捷。',
        chinaChemicalEngineering: '中国化工第三建设有限公司',
        chinaChemicalEngineeringDescription: '室内天花板使用高品质玻璃纤维吸音产品，采用优雅悬挂安装和高品质大面积转换效果，创造简单时尚的天花板空间。特点为外观优美，显著减少室内背景噪音并改善混响时间。',
        kazakhstanBallroomAcademy: '哈萨克斯坦国际芭蕾舞学院',
        kazakhstanBallroomAcademyDescription: '专为芭蕾舞学院设计的天花板系统，采用Accord垂直吊挂面板系列。该系统提供卓越的声学控制和美学吸引力，创造出适合舞蹈表演和训练的理想环境。',
        deMontfortUniversity: '德蒙福特大学办公楼',
        deMontfortUniversityDescription: '现代大学办公楼采用先进天花板系统，使用Yashang系列产品。开放天花板设计创造出宽敞现代的工作空间，同时保持卓越的声学性能和视觉吸引力。',
        systemType: '系统类型',
        panelSize: '面板尺寸',
        loadCapacity: '负载能力',
        lightReflectance: '光反射率',
        wallArea: '墙面面积',
        wallAreaValue: '60m²',
        wallPanelType: '墙面面板类型',
        wallPanelTypeValue: '北洋合越系列 25mm 声学面板',
        ceilingArea: '天花板面积',
        ceilingAreaValue: '256m²',
        ceilingPanelType: '天花板面板类型',
        ceilingPanelTypeValue: '北洋雅尚系列 50mm 垂直吊挂面板系统 (网格图案)',
        reverberationTime: '混响时间 (中频)',
        reverberationBefore: '2.48s → 0.7s',
        speechTransmission: '语音传输指数',
        speechTransmissionBefore: '0.43 (差) → 0.73 (好)',
        applicationArea: '应用区域',
        publicArea: '公共区域',
        productUsed: '使用的产品',
        beiyangYashangSeries: '北洋雅尚垂直吊挂面板系列',
        suspensionSystem: '悬挂系统',
        hardConnectionSystem: '硬连接悬挂系统',
        performanceFeatures: '性能特点',
        stabilityWindEarthquake: '稳定性、抗风性、抗震性和耐久性',
        designFeature: '设计特点',
        variousShapesColors: '各种形状和颜色',
        beiyangYashangWaterFlat: '北洋雅尚水平吊挂面板系列',
        acousticBenefit: '声学效益',
        noiseReductionClarity: '降低噪音和提高语音清晰度',
        officeActivityCenter: '办公活动中心和办公室',
        beiyangTuoshiOpenCeiling: '北洋图时开放天花板系列',
        soundPressureReduction: '声压级降低',
        lightweightEasyMaintenance: '轻质材料、安装方便和维护便捷',
        inpatientCorridorClinic: '住院病房走廊、门诊诊所',
        badmintonStadium: '羽毛球场',
        beiyangYashangWaterFlatSeries: '北洋雅尚水平吊挂面板系列',
        elegantSuspensionInstallation: '优雅悬挂安装',
        backgroundNoiseReduction: '降低背景噪音和改善混响时间',
        productSpecs: '产品规格',
        kazakhstanProductSpecs: '600×2400×200mm',
        productSeries: '产品系列',
        kazakhstanProductSeries: 'Accord - 垂直吊挂面板系列',
        kazakhstanApplicationArea: '芭蕾舞厅',
        acousticSoundAbsorption: '声学吸音和混响控制',
        hkustProductSpecs: '600×1500×20mm',
        hkustProductSeries: 'Tuoshi - Yingji Series',
        hkustApplicationArea: '教学楼走廊',
        concertHall: '音乐厅',
        performanceSpace: '表演空间',
        acousticControl: '声学控制',
        university: '大学',
        educationalInstitution: '教育机构',
        hospital: '医院',
        healthcareFacility: '医疗设施',
        corporateOffice: '企业办公室',
        businessFacility: '商业设施',
        auditorium: '礼堂',
        metroStation: '地铁站',
        publicTransport: '公共交通',
        sportsFacility: '体育设施',
        badmintonHall: '羽毛球场',
        ballroomDance: '芭蕾舞学院',
        locationCentralMusicHall: '波兰',
        locationChongqingUniversity: '重庆, 中国',
        locationSeoulMetroLine9: '首尔, 韩国',
        locationBeijingLenovoHQ: '北京, 中国',
        locationShenzhenLuohuHospital: '深圳, 中国',
        locationChinaChemicalEngineering: '深圳, 中国',
        locationKazakhstanBallroomAcademy: '阿拉木图, 哈萨克斯坦',
        locationHKUST: '香港',
        locationDeMontfortUniversity: '莱斯特, 英国',
        library: '图书馆',
        pudongAirport: '浦东国际机场',
        pudongAirportDescription: '浦东国际机场安装钢制架空地板系统，总面积为5600m²。高性能架空地板系统设计用于高流量机场环境。',
        shenzhenHnbc: '深圳HNBC总部',
        shenzhenHnbcDescription: '深圳HNBC总部安装钢制架空地板系统，总面积为40000m²。大型商业安装提供优秀结构支持。',
        macauStudioCity: '澳门工作室城',
        macauStudioCityDescription: '澳门工作室城娱乐综合体安装PARETE钢制架空地板（FS2000）系统，总面积为12000m²。高端架空地板系统设计用于娱乐场所。',
        macauGalaxy3A: '澳门银河3A游戏区',
        macauGalaxy3ADescription: '澳门银河3A游戏区安装PARETE钢制架空地板FS2000系统，总面积为2200m²。高端架空地板系统专为游戏和娱乐设施设计，于2021年10月供应。',
        mgmCotai: 'MGM Cotai',
        mgmCotaiDescription: 'MGM Cotai综合度假村安装PARETE钢制架空地板（FS1250）系统，总面积为650m²。高性能架空地板系统设计用于豪华酒店和游戏设施。',
        floorType: '地板类型',
        projectQuantity: '项目数量',
        floorApplication: '地板应用',
        pudongQuantity: '5600 m²',
        hnbcQuantity: '40000 m²',
        macauQuantity: '12000 m²',
        macauProduct: 'PARETE钢制架空地板 (FS2000)',
        macauGalaxy3AProduct: 'PARETE钢制架空地板 FS2000',
        macauGalaxy3AQuantity: '2200 m²',
        macauGalaxy3ASupplyDate: '2021年10月',
        mgmCotaiProduct: 'PARETE钢制架空地板 (FS1250)',
        mgmCotaiQuantity: '650 m²',
        airportTerminal: '机场航站楼',
        corporateHeadquarter: '企业总部',
        entertainmentVenue: '娱乐场所',
        gamingArea: '游戏区',
        integratedResort: '综合度假村',
        highLoadStructural: '高负载能力及结构支持',
        supplyDate: '供应日期',
        airport: '机场',
        transportHub: '交���枢纽',
        structuralSupport: '结构支持',
        commercialBuilding: '商业建筑',
        officeSpace: '办公空间',
        entertainmentComplex: '娱乐综合体',
        studioSpace: '工作室空间',
        casino: '赌场',
        gamingFacility: '游戏设施',
        resortFacility: '度假村设施',
        locationPudongAirport: '上海, 中国',
        locationShenzhenHnbc: '深圳, 中国',
        locationMacauStudioCity: '澳门',
        locationMacauGalaxy3A: '澳门',
        locationMgmCotai: '澳门'
    }
};

const JOB_REFERENCE_CATEGORIES = [
    { id: 'all', key: 'jobReference.filter.all' },
    { id: 'Raised Floor System', key: 'jobReference.category.raisedFloor' },
    { id: 'Ceiling System', key: 'jobReference.category.ceiling' }
];

let activeJobReferenceCategory = 'all';

function getJobReferenceLanguage() {
    const lang = document.documentElement.getAttribute('data-language') || 'EN';
    return JOB_REFERENCE_STRINGS[lang] ? lang : 'EN';
}

function getJobReferenceText(key, lang) {
    const current = JOB_REFERENCE_STRINGS[lang] || JOB_REFERENCE_STRINGS.EN;
    return current[key] || JOB_REFERENCE_STRINGS.EN[key] || key;
}

function getSharedTranslation(key) {
    return typeof t === 'function' ? t(key) : key;
}

function escapeJobReferenceHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function getCategoryLabel(category) {
    const match = JOB_REFERENCE_CATEGORIES.find(item => item.id === category);
    return match ? getSharedTranslation(match.key) : category;
}

function getSearchText(item, lang) {
    const fields = [
        getJobReferenceText(item.nameKey, lang),
        getJobReferenceText(item.descKey, lang),
        getJobReferenceText(item.locationKey, lang),
        getCategoryLabel(item.category),
        ...item.properties.flatMap(([labelKey, valueKey]) => [
            getJobReferenceText(labelKey, lang),
            getJobReferenceText(valueKey, lang)
        ]),
        ...item.applications.map(key => getJobReferenceText(key, lang))
    ];
    return fields.join(' ').toLowerCase();
}

function renderJobReferenceFilters() {
    const filters = document.getElementById('job-reference-filters');
    if (!filters) return;

    filters.innerHTML = JOB_REFERENCE_CATEGORIES.map(category => {
        const isActive = category.id === activeJobReferenceCategory;
        const classes = isActive
            ? 'bg-orange-500 text-white border-orange-500 shadow-sm'
            : 'bg-white text-slate-700 border-slate-200 hover:border-orange-300 hover:text-orange-600';
        return `
            <button type="button"
                    class="job-reference-filter px-4 py-2 rounded-full border text-sm font-semibold transition-colors ${classes}"
                    data-category="${escapeJobReferenceHtml(category.id)}"
                    aria-pressed="${isActive ? 'true' : 'false'}">
                ${escapeJobReferenceHtml(getSharedTranslation(category.key))}
            </button>
        `;
    }).join('');

    filters.querySelectorAll('.job-reference-filter').forEach(button => {
        button.addEventListener('click', () => {
            activeJobReferenceCategory = button.getAttribute('data-category') || 'all';
            renderJobReferencesPage();
        });
    });
}

function renderJobReferenceCard(item, lang) {
    const name = getJobReferenceText(item.nameKey, lang);
    const description = getJobReferenceText(item.descKey, lang);
    const location = getJobReferenceText(item.locationKey, lang);
    const categoryLabel = getCategoryLabel(item.category);
    const properties = item.properties.map(([labelKey, valueKey]) => `
        <div class="bg-slate-50 border border-slate-100 rounded-md p-3">
            <dt class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">${escapeJobReferenceHtml(getJobReferenceText(labelKey, lang))}</dt>
            <dd class="text-sm text-slate-900 leading-snug">${escapeJobReferenceHtml(getJobReferenceText(valueKey, lang))}</dd>
        </div>
    `).join('');
    const applications = item.applications.map(key => `
        <span class="inline-flex items-center rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-xs font-semibold text-orange-700">
            ${escapeJobReferenceHtml(getJobReferenceText(key, lang))}
        </span>
    `).join('');

    return `
        <article class="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-sm hover:shadow-xl hover:border-orange-300 transition-all">
            <div class="aspect-[4/3] overflow-hidden bg-slate-100">
                <img src="${escapeJobReferenceHtml(item.image)}"
                     alt="${escapeJobReferenceHtml(name)}"
                     loading="lazy"
                     class="w-full h-full object-cover hover:scale-105 transition-transform duration-300">
            </div>
            <div class="p-6">
                <div class="flex flex-wrap items-start justify-between gap-3 mb-4">
                    <h2 class="text-xl font-semibold text-slate-900 leading-snug">${escapeJobReferenceHtml(name)}</h2>
                    <span class="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">${escapeJobReferenceHtml(categoryLabel)}</span>
                </div>
                <p class="text-slate-600 text-sm leading-6 mb-4">${escapeJobReferenceHtml(description)}</p>
                <div class="flex items-center gap-2 text-sm text-slate-600 mb-5">
                    <svg class="w-4 h-4 text-orange-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    </svg>
                    <span>${escapeJobReferenceHtml(location)}</span>
                </div>
                <div class="mb-5">
                    <h3 class="text-sm font-semibold text-slate-900 mb-3">${escapeJobReferenceHtml(getSharedTranslation('jobReference.properties'))}</h3>
                    <dl class="grid grid-cols-1 sm:grid-cols-2 gap-2">${properties}</dl>
                </div>
                <div>
                    <h3 class="text-sm font-semibold text-slate-900 mb-3">${escapeJobReferenceHtml(getSharedTranslation('jobReference.applications'))}</h3>
                    <div class="flex flex-wrap gap-2">${applications}</div>
                </div>
            </div>
        </article>
    `;
}

function renderJobReferencesPage() {
    const grid = document.getElementById('job-reference-grid');
    if (!grid) return;

    const lang = getJobReferenceLanguage();
    const searchInput = document.getElementById('job-reference-search');
    const query = searchInput ? searchInput.value.trim().toLowerCase() : '';
    const visibleItems = JOB_REFERENCE_ITEMS.filter(item => {
        const matchesCategory = activeJobReferenceCategory === 'all' || item.category === activeJobReferenceCategory;
        const matchesQuery = query === '' || getSearchText(item, lang).includes(query);
        return matchesCategory && matchesQuery;
    });

    renderJobReferenceFilters();
    grid.innerHTML = visibleItems.map(item => renderJobReferenceCard(item, lang)).join('');

    const noResults = document.getElementById('job-reference-no-results');
    if (noResults) {
        noResults.classList.toggle('hidden', visibleItems.length > 0);
    }
}

function initializeJobReferencesPage() {
    if (!document.getElementById('job-reference-grid')) return;

    const searchInput = document.getElementById('job-reference-search');
    if (searchInput) {
        searchInput.addEventListener('input', renderJobReferencesPage);
    }

    renderJobReferencesPage();
}

document.addEventListener('DOMContentLoaded', initializeJobReferencesPage);
document.addEventListener('sunfly:languagechange', renderJobReferencesPage);
