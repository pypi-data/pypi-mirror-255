# CHANGELOG



## v5.0.1 (2024-02-06)

### Documentation

* docs(README.md): Fix PyPI version badge ([`e55b88f`](https://github.com/Rizhiy/pycs/commit/e55b88fc6d77a5e5dee9c0d24980f848384b2d09))

### Fix

* fix(node.py): fix type for load_or_static ([`33866cc`](https://github.com/Rizhiy/pycs/commit/33866cc49b74a62002123ab54e6d1a4a57a5ff49))


## v5.0.0 (2024-01-31)

### Breaking

* refactor: change how cfg variable in config files are initialised to make it easier to parse and less restrictive

BREAKING CHANGE: `cfg = CN(cfg)` is no longer allowed, use `cfg = schema.init_cfg()` or `cfg = cfg.clone()` ([`a171ed7`](https://github.com/Rizhiy/pycs/commit/a171ed77052a630f61506de212932ebe548bd5e4))

* refactor: change to use &#39;schema&#39; as variable name for cfg schema

BREAKING CHANGE: Now only initialised config can be imported as cfg ([`488109e`](https://github.com/Rizhiy/pycs/commit/488109e6f197c024ba2c5106c257765139340ffd))

### Feature

* feat(utils.py): Add warning when extending config file without clone and add tests ([`6ea200d`](https://github.com/Rizhiy/pycs/commit/6ea200d88cb5b54635021bf0c0d22463f53068cc))

* feat(node.py): Add new_allowed as a property ([`f5d7a0c`](https://github.com/Rizhiy/pycs/commit/f5d7a0c75bbeea21aba14640080ee1f99d555342))

### Fix

* fix(pyproject.toml): Add missing isort dependency ([`d7ed00f`](https://github.com/Rizhiy/pycs/commit/d7ed00f7fa2b24f48a4d7c8c120daf29603bac52))


## v4.5.0 (2024-01-29)

### Feature

* feat(node.py): Add helper function propagate_changes ([`d125652`](https://github.com/Rizhiy/pycs/commit/d12565220f3b3372fb8867d5cbcc98e05429978b))


## v4.4.1 (2024-01-25)

### Chore

* chore(node.py): Improve one error message ([`27ee2ef`](https://github.com/Rizhiy/pycs/commit/27ee2ef6021f428235b636390b4fc175e920dfb1))

* chore(test_helpers.py): Ignore S404 ([`9244a4c`](https://github.com/Rizhiy/pycs/commit/9244a4c9313b39b1ff150dc78e85d80baf9d6648))

### Ci

* ci(test_and_version.yml): add codecov ([`788a290`](https://github.com/Rizhiy/pycs/commit/788a29091fb697d306aa8ed92cb738c8c96b61b3))

### Documentation

* docs(README.md): Add python version and pypi package version badges ([`171c2a4`](https://github.com/Rizhiy/pycs/commit/171c2a4f21ff9cc626d58bbb854188c316c7302a))

* docs(README.md): add codecov badge ([`b14a352`](https://github.com/Rizhiy/pycs/commit/b14a35214e02273365da9adb596c145e52f3acf0))

### Fix

* fix(transforms.py): Fix loading of empty string in LoadFromEnvVars ([`2d3b144`](https://github.com/Rizhiy/pycs/commit/2d3b144bb4e26e38a9735dd79fb89a1eb964feda))


## v4.4.0 (2024-01-11)

### Chore

* chore(test_good.py): Ignore false positive rule ([`6740f4b`](https://github.com/Rizhiy/pycs/commit/6740f4b6a9208f2eaf32a9725cdfa45c657e1187))

### Feature

* feat(transforms.py): Add transform to load from AWS Secrets Manager ([`ce5580f`](https://github.com/Rizhiy/pycs/commit/ce5580fc0b1c184001e53b2cffa710b0f376e740))

### Style

* style: Format with ruff ([`32a2e2e`](https://github.com/Rizhiy/pycs/commit/32a2e2ee47a8ebef9e1325ebe2b3aba3629aebea))

### Test

* test(pyproject.toml): add &#39;aws&#39; extra to dev extra ([`736fd2f`](https://github.com/Rizhiy/pycs/commit/736fd2f9ec6b60d2949e61e954ddb054b7b17044))


## v4.3.0 (2024-01-10)

### Documentation

* docs(README.md): Lint markdown ([`382b95f`](https://github.com/Rizhiy/pycs/commit/382b95fe0b9aade99b679ae79cc6ff85d0b8b6a5))

### Feature

* feat(transforms.py): Add transform for AWSAppConfig ([`5aee69f`](https://github.com/Rizhiy/pycs/commit/5aee69fa90924b919a687c573dbc4b3f51cbdd85))

### Refactor

* refactor(node.py): improve type annotations ([`b7dfa4e`](https://github.com/Rizhiy/pycs/commit/b7dfa4e307cd16898196eec8ff28891bb4ba8a8c))


## v4.2.0 (2023-12-23)

### Feature

* feat(node.py): Properly implement .update() and add tests ([`9b57103`](https://github.com/Rizhiy/pycs/commit/9b57103dcfa85394e6f397facba4b8cf8632f144))

### Fix

* fix(pyproject.toml): Decrease minimum python version back to 3.9 ([`22fe49c`](https://github.com/Rizhiy/pycs/commit/22fe49c54bf0ff7a484788e5f6c71f845bcab865))

### Style

* style: add style configurations and format various files ([`d137094`](https://github.com/Rizhiy/pycs/commit/d137094c1ce724bdb255fe2105d609a4538a6129))


## v4.1.0 (2023-12-21)

### Chore

* chore(pyproject.toml): Re-organise sections ([`351fe27`](https://github.com/Rizhiy/pycs/commit/351fe27df4e692779b37db1e45f5f9ac20aa0e63))

* chore: Rename package to pycs ([`a6ef804`](https://github.com/Rizhiy/pycs/commit/a6ef804c3d14c2a51e5518742819e5e4795acbac))

### Documentation

* docs(README.md): Shorten dev section ([`7ca625f`](https://github.com/Rizhiy/pycs/commit/7ca625f80df06d4daff44a4f51d34f8b06eccd01))

* docs(README.md): Update links ([`1d6f497`](https://github.com/Rizhiy/pycs/commit/1d6f4978372b697fd8fb08355f14192fd28c085c))

* docs(REAMDME.md): Add acknowledgements ([`4db26fa`](https://github.com/Rizhiy/pycs/commit/4db26faec42d82913d29f1825adeaa3c7381eee8))

* docs(README.md): Add info about commitizen ([`bf445e3`](https://github.com/Rizhiy/pycs/commit/bf445e3e5acacc80047a23319521f67761790cd3))

### Feature

* feat(node.py): add load_or_static helper method ([`be203e4`](https://github.com/Rizhiy/pycs/commit/be203e47f44d6a9141e25562367602de2806c683))


## v4.0.1 (2023-12-18)

### Chore

* chore(pyproject.toml): Add maintainers section ([`d1a6344`](https://github.com/Rizhiy/pycs/commit/d1a6344a7c15db2714d630bc9f71ddf148773c30))

### Documentation

* docs(README.md): Add note about ruff ([`8acd18b`](https://github.com/Rizhiy/pycs/commit/8acd18bcf97be00d7c74cf21ec0d0e6cf0d9923b))

* docs(README.md): Add note about commit messages ([`82f1b40`](https://github.com/Rizhiy/pycs/commit/82f1b4085eee68dae53dcecb0149eab16dee4e10))

* docs(README.md): Update badge ([`2a2e7ad`](https://github.com/Rizhiy/pycs/commit/2a2e7ad3c5145d60e1b35bb5bbcbda38c903fb7b))

### Fix

* fix: Clean-up ([`57fdc3e`](https://github.com/Rizhiy/pycs/commit/57fdc3ef278d36d3ba72db484498821dda59a1b2))


## v4.0.0 (2023-12-18)

### Breaking

* chore: Rename to rizhiy-cfg as cfg is taken on PyPI

BREAKING CHANGE: Rename ([`e5050b5`](https://github.com/Rizhiy/pycs/commit/e5050b5d0de80a6e1ede6fea02e2d762b2a172b7))

* feat: Rename package to cfg

BREAKING CHANGE: Rename package to cfg ([`86d47d5`](https://github.com/Rizhiy/pycs/commit/86d47d51569d0948d38b294dea6c3b803a02f3a5))

### Chore

* chore(test_and_publish.yml): Add publish step

chore(test_and_publish.yml): Set up automatic version update

chore(pyproject.toml): Trying to fix install

chore(test_and_publish.yml): Fix step name

chore(pyproject.toml): Try pushing release without token

chore(test_and_publish.yml): Try simple push

chore(test_and_publish.yml): Add write permissions

chore(publish.yml): Move publish into separate workflow and update rules

chore(test_and_version.yml): Use PAT

chore(workflows): Update conditions and variables

chore(workflows): Update tag rules

chore: Debugging skipped step

chore(workflows): Filter whole workflows by tag

chore(workflows): Try match on commit message

chore(publish.yml): Add FLIT_USERNAME

chore(test_and_version.yml): Downgrade semantic-release version

chore(test_and_version.yml): Add semantic release ([`2f455fe`](https://github.com/Rizhiy/pycs/commit/2f455fee49b5e6188cf2eaef64b8828071b97bf1))

* chore(test.yml): Add ruff to github actions ([`1d53cac`](https://github.com/Rizhiy/pycs/commit/1d53cac24d689c318dac520f6ec8d937610881dc))

* chore: Fix ruff errors in the main package ([`bc51574`](https://github.com/Rizhiy/pycs/commit/bc5157423746e4e76435ff68310475ca2542b5a0))

* chore: Add ruff rules and fix errors in tests ([`943937d`](https://github.com/Rizhiy/pycs/commit/943937de1259a47459e139eca47a6187a327900e))

* chore(pyproject.toml): Define ruff rules ([`b4385e6`](https://github.com/Rizhiy/pycs/commit/b4385e6c083727a3c6d0ba05dca861a6555dccd8))

* chore(python-package.yml): Fix test install ([`aaae76f`](https://github.com/Rizhiy/pycs/commit/aaae76f0387422fbb7a5f949b8cc2666141e30b9))

* chore(python-package.yml): Add pytest on CI ([`c8b4462`](https://github.com/Rizhiy/pycs/commit/c8b4462aa1b96ec3ff2587380605d59d399d9b12))

### Documentation

* docs(README.md): Update ([`e993ad5`](https://github.com/Rizhiy/pycs/commit/e993ad50b88919daa89a97444ce09d8ab5f4fcfc))


## v3.1.2 (2023-07-03)

### Unknown

* 3.1.2

Feature
* **helpers.py:** Add mkdir and base_dir options to get_output_dir (68e2e91) ([`0af1f25`](https://github.com/Rizhiy/pycs/commit/0af1f256fe90c94db538f9c257674583ca419729))

* imp(helpers.py): Add mkdir and base_dir options to get_output_dir ([`68e2e91`](https://github.com/Rizhiy/pycs/commit/68e2e9130f9d9e28a770248c6a90e82f6a81c2b7))


## v3.1.1 (2023-06-29)

### Unknown

* 3.1.1

Feature
* **node.py:** Freeze schema of assigned nodes if parent schema is frozen (553846b) ([`6b03907`](https://github.com/Rizhiy/pycs/commit/6b03907f1d18e7e8a37649722ed50c8854c8ea16))

* imp(node.py): Freeze schema of assigned nodes if parent schema is frozen ([`553846b`](https://github.com/Rizhiy/pycs/commit/553846b492cec28bcda2c26bb6bb0220df88986b))


## v3.1.0 (2023-06-29)

### Feature

* feat(helpers.py): Add helper function to get path of the output dir for configs ([`c46018f`](https://github.com/Rizhiy/pycs/commit/c46018f9e6b29e9052003fb970d9ef3cf15f0a9c))

### Unknown

* 3.1.0

Feature
* **helpers.py:** Add helper function to get path of the output dir for configs (c46018f) ([`77ea447`](https://github.com/Rizhiy/pycs/commit/77ea4471350572a5cc55c7e4c04389d14417799b))


## v3.0.0 (2023-05-31)

### Unknown

* 3.0.0

Feature
* **node.py:** Change static_init() to return cfg rather than modify in-place (1f8345f)

Breaking
* cfg.static_init() now returns the initialised config rather than initialising in-place. (1f8345f) ([`0f836c2`](https://github.com/Rizhiy/pycs/commit/0f836c246b79757a21c2e8c20410af34d33f02cd))

* imp(node.py): Change static_init() to return cfg rather than modify in-place

BREAKING CHANGE: cfg.static_init() now returns the initialised config
rather than initialising in-place. ([`1f8345f`](https://github.com/Rizhiy/pycs/commit/1f8345fd127af4f4c70a8785d2b7dd401c8df1a6))


## v2.3.0 (2023-01-15)

### Feature

* feat(node.py): Add static_init() ([`b6d86ff`](https://github.com/Rizhiy/pycs/commit/b6d86ff5e82ab9eeb3e6865b3101e8c2b9c50b68))

### Test

* test(.gitlab-ci.yml): Remove check-yamlfix, since it is now in template ([`cf21b6a`](https://github.com/Rizhiy/pycs/commit/cf21b6a6da2b7f353e3931ce6fecf4a0254d5f3b))

* test(requirements_frozen.txt): Update ([`80d8e3e`](https://github.com/Rizhiy/pycs/commit/80d8e3efcbf00992917f2cee2789a74dc9c99067))

* test(pyproject.toml): Change tests to test ([`9d42d26`](https://github.com/Rizhiy/pycs/commit/9d42d266457825ca1517d7d34119ca6ddd29c605))

### Unknown

* 2.3.0

Feature
* **node.py:** Add static_init() (b6d86ff)
* **transforms.py:** Expand user if path is provided as a string in LoadFromFile (529f088) ([`4e64a46`](https://github.com/Rizhiy/pycs/commit/4e64a46f7b796417a7fa63dd7ca72dcaf27a12df))

* imp(transforms.py): Expand user if path is provided as a string in LoadFromFile ([`529f088`](https://github.com/Rizhiy/pycs/commit/529f08872c30f98398f687699cae848c734dbb8d))


## v2.2.1 (2023-01-06)

### Fix

* fix(.gitlab-ci.yml): Update to gitlab.com template ([`ea795fd`](https://github.com/Rizhiy/pycs/commit/ea795fd7481913a51924aecd95c02851f625d5f2))

### Test

* test(requirements_frozen.txt): Update to use gitlab.com index ([`790de36`](https://github.com/Rizhiy/pycs/commit/790de368bb1a0912b8b8f3138e3acff445952204))

### Unknown

* 2.2.1

Fix
* **.gitlab-ci.yml:** Update to gitlab.com template (ea795fd) ([`abea5ff`](https://github.com/Rizhiy/pycs/commit/abea5ff50f4928d7f9491d00781e71db31b07078))


## v2.2.0 (2022-06-29)

### Feature

* feat(node.py): Allow re-assigning empty node to another node ([`99eef8e`](https://github.com/Rizhiy/pycs/commit/99eef8e5861ceb954767b14ef9db1b14960f6625))

### Unknown

* 2.2.0

Feature
* **node.py:** Allow re-assigning empty node to another node (99eef8e)
* **leaf.py:** Add type of wrong value to error message (df88398) ([`68973dc`](https://github.com/Rizhiy/pycs/commit/68973dc281fc178b90dc299142a2d08f32993548))

* imp(leaf.py): Add type of wrong value to error message ([`df88398`](https://github.com/Rizhiy/pycs/commit/df883989d6394aa350566b08494c346f52c4ddec))


## v2.1.2 (2022-06-23)

### Unknown

* 2.1.2

Feature
* Change to dynamically calculating full_key (ccf5eff) ([`f76eb85`](https://github.com/Rizhiy/pycs/commit/f76eb8548a0221fbe8c858f7adb41b310d5e072a))

* imp: Change to dynamically calculating full_key ([`ccf5eff`](https://github.com/Rizhiy/pycs/commit/ccf5effa12c32c3391c5249ca19c195d78ea55ff))


## v2.1.1 (2022-06-07)

### Chore

* chore: mypy config ([`23e4989`](https://github.com/Rizhiy/pycs/commit/23e4989514e87697f7e0b47eaf97b0a2c6e12767))

* chore: enable doctest modules through pytest config ([`b279a61`](https://github.com/Rizhiy/pycs/commit/b279a619c0a1d1bcafab2c381f05361b2badda99))

* chore: `py.typed`, `yamlfix`, updated pins ([`29ac016`](https://github.com/Rizhiy/pycs/commit/29ac0164914d57a1f6f9eccad9be17b0b50fcf00))

* chore: flit-based packaging ([`c874945`](https://github.com/Rizhiy/pycs/commit/c8749456f704fc59ea0120585524e19efca551bc))

### Refactor

* refactor: flake8-guided style fixes ([`c0bae7e`](https://github.com/Rizhiy/pycs/commit/c0bae7e4c9ee516497d0d994203dcde450d7529b))

* refactor: use basic containers for typing ([`1e3ef1e`](https://github.com/Rizhiy/pycs/commit/1e3ef1ee3ac820f83c7bca5fcc2d66eb03d49680))

### Style

* style: Format ([`ffba55a`](https://github.com/Rizhiy/pycs/commit/ffba55af986da776e5987f85e994f61bab1b450f))

### Unknown

* 2.1.1

Feature
* **node.py:** Add warning regarding transforming without freezing schema (fa01135) ([`ba1d6c2`](https://github.com/Rizhiy/pycs/commit/ba1d6c27e091ee913201a29df54c6824a3b91582))

* imp(node.py): Add warning regarding transforming without freezing schema ([`fa01135`](https://github.com/Rizhiy/pycs/commit/fa01135af16e87635c777238901e7780efa9a301))

* Merge branch &#39;refactor_style_fixes&#39; into &#39;master&#39;

refactor: flake8-guided style fixes

See merge request utilities/ntc!46 ([`2a331b7`](https://github.com/Rizhiy/pycs/commit/2a331b7766915435d9f771fda455b630d140ff1e))

* Merge branch &#39;chore_refactor1&#39; into &#39;master&#39;

chore: `py.typed`, `yamlfix`, updated pins, pytest config

See merge request utilities/ntc!45 ([`f21f0a9`](https://github.com/Rizhiy/pycs/commit/f21f0a920be84bc9bcfb826b9c8ce42544bf9881))

* Merge branch &#39;typing_basic_containers&#39; into &#39;master&#39;

refactor: use basic containers for typing

See merge request utilities/ntc!44 ([`6faa0c0`](https://github.com/Rizhiy/pycs/commit/6faa0c0f07719f9ae8225a292c19b4046d819310))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

chore: flit-based packaging

See merge request utilities/ntc!42 ([`c6f8f54`](https://github.com/Rizhiy/pycs/commit/c6f8f541dce1ba00bc530fe6994a603dfaa5031f))


## v2.1.0 (2022-02-03)

### Chore

* chore: fix for `ntu` -&gt; `nt-dev` ([`b7fa8ac`](https://github.com/Rizhiy/pycs/commit/b7fa8acd19928528da31ce84edea7f531c9fa888))

### Feature

* feat: support basic `typing` containers as leaf types ([`579b1ea`](https://github.com/Rizhiy/pycs/commit/579b1ea1d2bfd7a1eaee61d46eb2ba7c12c97417))

### Test

* test: mypy ([`8143e24`](https://github.com/Rizhiy/pycs/commit/8143e2452d664696ad2ec6eac6bcb19ac93c1251))

### Unknown

* 2.1.0

Feature
* Support basic `typing` containers as leaf types (579b1ea) ([`10c21c2`](https://github.com/Rizhiy/pycs/commit/10c21c2cd786ef149169e4257ee815b8dd5d48c8))

* Merge branch &#39;hhell/stuff1c&#39; into &#39;master&#39;

feat: support basic `typing` containers as leaf types

See merge request utilities/ntc!43 ([`4c19ea0`](https://github.com/Rizhiy/pycs/commit/4c19ea0f93cb3ec6fcc4209b68b16aacd4e8f605))

* Merge branch &#39;hhell/mypy3&#39; into &#39;master&#39;

test: mypy

See merge request utilities/ntc!41 ([`a02aac9`](https://github.com/Rizhiy/pycs/commit/a02aac987a6784e658a749e1f086b54503216318))

* Merge branch &#39;hhell/testsfix&#39; into &#39;master&#39;

chore: fix for `ntu` -&gt; `nt-dev`

See merge request utilities/ntc!39 ([`7428c1c`](https://github.com/Rizhiy/pycs/commit/7428c1c59b1a2ef7dd7e7e05a01357c9ee561dca))


## v2.0.4 (2021-12-04)

### Chore

* chore(tests): whitelist doctest-modules ([`be7d294`](https://github.com/Rizhiy/pycs/commit/be7d2943ed01d52116da8aaeecd33fcb993e75cc))

* chore(tests): updated gitlab config ([`7456c1c`](https://github.com/Rizhiy/pycs/commit/7456c1cb29e7f5cea0b898cc8a461a0d17e864a3))

### Unknown

* 2.0.4

Feature
* **node.py:** Allow setting custom root name (9e8ed29)
* **node:** Take all directories under `config/` as part of the name (59935ef) ([`8a094e8`](https://github.com/Rizhiy/pycs/commit/8a094e8b6b21cbacff767875afb4d66fb40b4b83))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

imp(node): take all directories under `config/` as part of the name

See merge request utilities/ntc!34 ([`94b4aca`](https://github.com/Rizhiy/pycs/commit/94b4aca9fe35912fd684138ffc5284e85516f805))

* imp(node.py): Allow setting custom root name ([`9e8ed29`](https://github.com/Rizhiy/pycs/commit/9e8ed29fee5a350d6b431bcad77473927030631c))

* imp(node): take all directories under `config/` as part of the name ([`59935ef`](https://github.com/Rizhiy/pycs/commit/59935efabab2c02a3659b8f8628947e5e729ca53))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

chore(tests): whitelist doctest-modules

See merge request utilities/ntc!33 ([`47d9044`](https://github.com/Rizhiy/pycs/commit/47d9044e5711bd751bba4a287a09b6332717a270))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

chore(tests): updated gitlab config

See merge request utilities/ntc!32 ([`b26f201`](https://github.com/Rizhiy/pycs/commit/b26f2019411c57d663de0df644a8bdcf2b5271f0))


## v2.0.3 (2021-11-25)

### Chore

* chore(tests): tests/requirements_frozen ([`88d7dc7`](https://github.com/Rizhiy/pycs/commit/88d7dc70a7fe8ddac69cc17f96ac584512adfab6))

### Unknown

* 2.0.3

Feature
* **utils:** A better error message in `_load_module` (efbddd6) ([`80f868a`](https://github.com/Rizhiy/pycs/commit/80f868a2c34aecdadcd81c75c9d5c725aa03e467))

* Merge branch &#39;hhell/stuff2&#39; into &#39;master&#39;

imp(utils): a better error message in `_load_module`

See merge request utilities/ntc!31 ([`f023177`](https://github.com/Rizhiy/pycs/commit/f023177f57455964cd3d3b2ac0d7ed5a1c5c2964))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

chore(tests): tests/requirements_frozen

See merge request utilities/ntc!30 ([`a7dfdbf`](https://github.com/Rizhiy/pycs/commit/a7dfdbf987dd7071f857b82a38bcc54e7c73660f))

* imp(utils): a better error message in `_load_module` ([`efbddd6`](https://github.com/Rizhiy/pycs/commit/efbddd65865c9fca0a94382e3efac218999b0634))


## v2.0.2 (2021-11-24)

### Chore

* chore(tests): use the new include for tests ([`2e8d0e3`](https://github.com/Rizhiy/pycs/commit/2e8d0e3564bd14097952373d828057033133b58a))

### Fix

* fix(tests): fix the tests/data ignoring ([`8d87090`](https://github.com/Rizhiy/pycs/commit/8d87090df7ffa6d6842451201a5ec787a727ef31))

### Unknown

* 2.0.2

Fix
* **tests:** Fix the tests/data ignoring (8d87090) ([`b8c0efc`](https://github.com/Rizhiy/pycs/commit/b8c0efc12926e17c3c6a76568e28c1522ac5561c))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

fix(tests): fix the tests/data ignoring

See merge request utilities/ntc!29 ([`cefd039`](https://github.com/Rizhiy/pycs/commit/cefd0398ad7aa2378765c9666504611d8e658e10))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

chore(tests): use the new include for tests

See merge request utilities/ntc!28 ([`a4d3951`](https://github.com/Rizhiy/pycs/commit/a4d3951711d01111c992168972d9d15cd89c4624))


## v2.0.1 (2021-11-18)

### Fix

* fix(tests): fix for `--doctest-modules` ([`7c5a306`](https://github.com/Rizhiy/pycs/commit/7c5a3067fb46f636e5ffd41ede8002b89994b712))

### Unknown

* 2.0.1

Fix
* **tests:** Fix for `--doctest-modules` (7c5a306) ([`e4e6033`](https://github.com/Rizhiy/pycs/commit/e4e603383da8f208b687cebaf7ff5d74efff2e07))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

fix(tests): fix for `--doctest-modules`

See merge request utilities/ntc!27 ([`3baec38`](https://github.com/Rizhiy/pycs/commit/3baec382043fbee36ed5ba6873370a8c7dfec357))


## v2.0.0 (2021-11-18)

### Breaking

* refactor(transforms): remove function-wrappers of transform classes

BREAKING CHANGE: deprecation cleanup ([`3b2c1bc`](https://github.com/Rizhiy/pycs/commit/3b2c1bc30deb57ba227ae33f8a6d450b45002bdc))

### Chore

* chore(ntc): setup.cfg ([`3d0211b`](https://github.com/Rizhiy/pycs/commit/3d0211b34424d29a4c3c0012e0b831144c7ac32e))

### Unknown

* 2.0.0

Breaking
* deprecation cleanup  (3b2c1bc) ([`3e5d7d5`](https://github.com/Rizhiy/pycs/commit/3e5d7d531242e2254d2fdfbf6e51955cc37f4b31))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

refactor(transforms): remove function-wrappers of transform classes

See merge request utilities/ntc!26 ([`ecdc69a`](https://github.com/Rizhiy/pycs/commit/ecdc69afb892989d18267cfb3fe0f7e16dc1a9a3))


## v1.3.1 (2021-11-16)

### Unknown

* 1.3.1

Feature
* **transforms:** Class-based transforms for better introspectability (4cac80f) ([`7f7953f`](https://github.com/Rizhiy/pycs/commit/7f7953fae59a76814589788309f50013b04fe8c0))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

imp(transforms): class-based transforms for better introspectability

See merge request utilities/ntc!25 ([`7e72773`](https://github.com/Rizhiy/pycs/commit/7e727737e1b6d4b857ed2c27c2a6f2fe068fef3c))

* imp(transforms): class-based transforms for better introspectability ([`4cac80f`](https://github.com/Rizhiy/pycs/commit/4cac80f537960d53c768d73e184de3842af62c7f))


## v1.3.0 (2021-11-15)

### Feature

* feat(transforms): `load_from_envvars` ([`8b185a2`](https://github.com/Rizhiy/pycs/commit/8b185a2deecf8257b98a3a61bfe9c18152981626))

### Unknown

* 1.3.0

Feature
* **transforms:** `load_from_envvars` (8b185a2)
* **transforms:** `load_from_key_value` minor improvements (e0dd6c8) ([`74f48b6`](https://github.com/Rizhiy/pycs/commit/74f48b6a2df7dfb08a46f89ee165f7d2a0218810))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

imp(transforms): `load_from_key_value` minor improvements, `load_from_envvars`

See merge request utilities/ntc!24 ([`1443fff`](https://github.com/Rizhiy/pycs/commit/1443fff1eea25122e7dcae6f355f61f7946632c6))

* imp(transforms): `load_from_key_value` minor improvements ([`e0dd6c8`](https://github.com/Rizhiy/pycs/commit/e0dd6c8c558a5ec91a604e29092408a4291fcc1d))


## v1.2.0 (2021-11-15)

### Feature

* feat(transforms): load_from_key_value ([`e7eed25`](https://github.com/Rizhiy/pycs/commit/e7eed25e80c4707d5cfb5217f153252dc0f49383))

### Refactor

* refactor(transforms): Minor value adjustment ([`05531e7`](https://github.com/Rizhiy/pycs/commit/05531e77c9620d7c7ead956b6c866958fea3ae8f))

### Unknown

* 1.2.0

Feature
* **transforms:** Load_from_key_value (e7eed25) ([`0b48d9e`](https://github.com/Rizhiy/pycs/commit/0b48d9eb46f18e6ff74f4b4b26223b0bf36e811b))

* Merge branch &#39;hhell/stuff&#39; into &#39;master&#39;

feat(transforms): load_from_key_value

See merge request utilities/ntc!23 ([`593486c`](https://github.com/Rizhiy/pycs/commit/593486c369cc34432740fc87256c5fc66f353a3b))


## v1.1.3 (2021-10-05)

### Documentation

* docs(README.md): Update budges ([`8602ee0`](https://github.com/Rizhiy/pycs/commit/8602ee03964814286794c74ac5f79f5160f405e4))

### Unknown

* 1.1.3

Feature
* **node.py:** Allow saving list of int, float or str (4f63f2c)

Documentation
* **README.md:** Update budges (8602ee0) ([`5ef5031`](https://github.com/Rizhiy/pycs/commit/5ef50317ef85bffed2c3d9f5655bc126f3f4dc8f))

* imp(node.py): Allow saving list of int, float or str ([`4f63f2c`](https://github.com/Rizhiy/pycs/commit/4f63f2c556b940689eb73bbde9347eeeccf20839))


## v1.1.2 (2021-10-04)

### Chore

* chore: Remove unused logger ([`51745da`](https://github.com/Rizhiy/pycs/commit/51745da8c15f64a1dc13ce9beaea131f3bfa5879))

### Documentation

* docs(README.md): add description example ([`ecc4a10`](https://github.com/Rizhiy/pycs/commit/ecc4a10e0477d4c8ba780ffd299b083d749edb88))

### Refactor

* refactor(all): rename module-level logger to LOGGER ([`c67cf2e`](https://github.com/Rizhiy/pycs/commit/c67cf2ed18b38d3606a29a3d668e1075c35158e3))

### Unknown

* 1.1.2

Feature
* **node.py:** Make get_raw() a public method and add test for full key on node assignment (fa3197b)

Documentation
* **README.md:** Add description example (ecc4a10) ([`07997c2`](https://github.com/Rizhiy/pycs/commit/07997c2226265a065916720f142839036b89ff90))

* imp(node.py): Make get_raw() a public method and add test for full key on node assignment ([`fa3197b`](https://github.com/Rizhiy/pycs/commit/fa3197b2419740c3a933a8ee0b62e98273e22f8a))

* Merge branch &#39;hhell/refactor&#39; into &#39;master&#39;

refactor(all): rename module-level logger to LOGGER

See merge request utilities/ntc!22 ([`c78f2a6`](https://github.com/Rizhiy/pycs/commit/c78f2a6590865a16c679d995f9d7e6168b1774bb))


## v1.1.1 (2021-08-10)

### Unknown

* 1.1.1

Feature
* **node.py:** Add pathlib.PosixPath to safe save types (96b1c84) ([`28a7023`](https://github.com/Rizhiy/pycs/commit/28a7023c90a547987d06caeb2b1212afa01934e9))

* imp(node.py): Add pathlib.PosixPath to safe save types ([`96b1c84`](https://github.com/Rizhiy/pycs/commit/96b1c84f425e21f10ba7f592526c0ed56c51e0a6))


## v1.1.0 (2021-08-09)

### Feature

* feat(interface.py): Add CfgSavable class so that user classes can be saved ([`d57ea1a`](https://github.com/Rizhiy/pycs/commit/d57ea1af3f1f9b22c90ea13aab11348575773e7c))

### Unknown

* 1.1.0

Feature
* **interface.py:** Add CfgSavable class so that user classes can be saved (d57ea1a) ([`d636ee7`](https://github.com/Rizhiy/pycs/commit/d636ee7fa0492bdc19b147b12032e4770983fca6))


## v1.0.2 (2021-08-09)

### Fix

* fix(node.py): Fix saving with clone ([`5ef9cde`](https://github.com/Rizhiy/pycs/commit/5ef9cde27184f89036037f3e8cb0fa0152547e69))

### Unknown

* 1.0.2

Fix
* **node.py:** Fix saving with clone (5ef9cde) ([`150b257`](https://github.com/Rizhiy/pycs/commit/150b25788f9f306d9de59a6761c7d8338f945e1d))


## v1.0.1 (2021-08-08)

### Fix

* fix(node.py): Only print last line in _module ([`8980f1f`](https://github.com/Rizhiy/pycs/commit/8980f1f701c625bed88e48c2f8a35601715d5cb5))

### Unknown

* 1.0.1

Fix
* **node.py:** Only print last line in _module (8980f1f) ([`4a68825`](https://github.com/Rizhiy/pycs/commit/4a68825bfc139d5021d66d0e310e6e8e22738d86))


## v1.0.0 (2021-08-08)

### Breaking

* feat: Allow changing simple types before saving

BREAKING CHANGE: Remove &#34;freezing&#34; functionality ([`1231ed8`](https://github.com/Rizhiy/pycs/commit/1231ed8486f76fdc9e5a04d523ceade6a552bf73))

### Unknown

* 1.0.0

Feature
* Allow changing simple types before saving (1231ed8)

Breaking
* Remove &#34;freezing&#34; functionality  (1231ed8) ([`d56857d`](https://github.com/Rizhiy/pycs/commit/d56857d6f89a50833cf1548e127ad24f23db19d3))


## v0.14.3 (2021-07-22)

### Chore

* chore(node.py): Add full key to __reduce__ error ([`ba95122`](https://github.com/Rizhiy/pycs/commit/ba95122a3661a832b785e25bbbd6ba9530a89b1b))

* chore(.gitlab-ci.yml): Correct test run condition ([`9e2d5fd`](https://github.com/Rizhiy/pycs/commit/9e2d5fd3fffeee87ba56ca6e87b9d3fbeba35c0e))

### Fix

* fix(transforms.py): Add default loader to load_from_file ([`07901b3`](https://github.com/Rizhiy/pycs/commit/07901b3d949eb3583ec47df2fe64c26ca3d16a50))

### Test

* test(.gitlab-ci.yml): Update to new template ([`887d3db`](https://github.com/Rizhiy/pycs/commit/887d3db3548102632a900f7a9507c1f3c7db7099))

### Unknown

* 0.14.3

Fix
* **transforms.py:** Add default loader to load_from_file (07901b3) ([`664ea59`](https://github.com/Rizhiy/pycs/commit/664ea59c8a06e770486b45ba6f5b0ba70f43f8e0))


## v0.14.2 (2021-05-11)

### Fix

* fix(transforms.py): Fix load_from_file and add tests ([`e47e809`](https://github.com/Rizhiy/pycs/commit/e47e80904bcdbe22fe3861701df4610c22644741))

### Unknown

* 0.14.2

Fix
* **transforms.py:** Fix load_from_file and add tests (e47e809) ([`31e03c1`](https://github.com/Rizhiy/pycs/commit/31e03c1dde38802e94a1ddc16c4104d9ce559587))


## v0.14.1 (2021-05-10)

### Fix

* fix(transforms.py): Add missing file handling ([`6fd373d`](https://github.com/Rizhiy/pycs/commit/6fd373da80d3f339e58d90146afac601781a980b))

### Unknown

* 0.14.1

Fix
* **transforms.py:** Add missing file handling (6fd373d) ([`1bfd6b4`](https://github.com/Rizhiy/pycs/commit/1bfd6b4782cba1749c460e9de38c37b50b859d55))


## v0.14.0 (2021-05-10)

### Feature

* feat(transforms.py): Add load_from_file transform ([`8834c43`](https://github.com/Rizhiy/pycs/commit/8834c43aaa332d339ab2030f6addefa26528e1c6))

### Style

* style(transforms.py): Format ([`9918263`](https://github.com/Rizhiy/pycs/commit/99182637f08d281ba9ea30f6437a1bc34b645e07))

### Unknown

* 0.14.0

Feature
* **transforms.py:** Add load_from_file transform (8834c43) ([`45af651`](https://github.com/Rizhiy/pycs/commit/45af6519d77d1fa3330d203c3336e68a6aa2bff3))


## v0.13.0 (2021-04-22)

### Chore

* chore: use base gitlab-ci ([`7bf71e0`](https://github.com/Rizhiy/pycs/commit/7bf71e0c886ca6f5828a454bbb9cda12d29252bc))

### Feature

* feat(node.py): add clear() ([`5059c2d`](https://github.com/Rizhiy/pycs/commit/5059c2dc3cb18f1f1988162dd2b32c5eb2b5318a))

### Refactor

* refactor(node.py): Change new_allowed logic ([`bc771a8`](https://github.com/Rizhiy/pycs/commit/bc771a8bb9da79e8d24e3fb0ac3b5b62b81f7bd3))

### Unknown

* 0.13.0

Feature
* **node.py:** Add clear() (5059c2d) ([`97cf6ab`](https://github.com/Rizhiy/pycs/commit/97cf6ab200900f7c350643e3e8945248f1f606b1))

* Merge branch &#39;ci/use-common-gitlab-ci&#39; into &#39;master&#39;

chore: use base gitlab-ci

See merge request utilities/ntc!21 ([`841af5c`](https://github.com/Rizhiy/pycs/commit/841af5cb0b3bb0d841d6c668ad039321ad0daa84))


## v0.12.2 (2021-04-09)

### Chore

* chore(__init__.py): Version bump ([`3c8cd46`](https://github.com/Rizhiy/pycs/commit/3c8cd467672805ac3cd7d3fb9100d233f5f7fb39))

* chore(__init__.py): Version bump ([`bb64570`](https://github.com/Rizhiy/pycs/commit/bb64570b5d2f07e470406d2bdfc973b508a3a64c))

* chore: add leaf path to error ([`7638a2b`](https://github.com/Rizhiy/pycs/commit/7638a2b8fb8c04428dac6064593aba05f08e2c80))

### Feature

* feat: write specific type in error ([`5677999`](https://github.com/Rizhiy/pycs/commit/567799904825b12fc75dbf65b52263f4c1e00bb8))

* feat: make meaningful errors for subclass ([`cd57231`](https://github.com/Rizhiy/pycs/commit/cd572314397e7496ab595841053fbcfb2c045e56))

* feat(description): nesting inheritance ([`ade781f`](https://github.com/Rizhiy/pycs/commit/ade781f99e755fa8185833a8f8385d714fb8baf8))

* feat: add description field ([`0f4a9e7`](https://github.com/Rizhiy/pycs/commit/0f4a9e71da2a9e7690e936d4ebcb99c34f2ceada))

* feat(ci): automate semantic release ([`d1e35a6`](https://github.com/Rizhiy/pycs/commit/d1e35a6beeab758a69c66a136a68c9448973e864))

* feat: Add pickle functionality ([`dd0f71e`](https://github.com/Rizhiy/pycs/commit/dd0f71ecba22a798175dee9bac1045f6bf0887d1))

* feat: helpful errors ([`1f601eb`](https://github.com/Rizhiy/pycs/commit/1f601eb4529357f7f2d8d7369143bfdef441d75b))

* feat: remove type set on assignment ([`d3ed0d7`](https://github.com/Rizhiy/pycs/commit/d3ed0d73ba1015feaa553beb1bc077886b4f9f76))

* feat: ntu format command ([`92df972`](https://github.com/Rizhiy/pycs/commit/92df9729b74adf8a89caca873a730b8eee130bf6))

* feat: organise tests ([`adae61f`](https://github.com/Rizhiy/pycs/commit/adae61f33caa9306365b07e8d54c03849a0fad9b))

* feat: add docs ([`1e1e805`](https://github.com/Rizhiy/pycs/commit/1e1e805f6317d3263b698b9085503d184d6b2f1f))

* feat: Add tests and remove unused code ([`9237242`](https://github.com/Rizhiy/pycs/commit/923724270caaead4d73de8a599ceebd708657ba4))

* feat: validators, transformers ([`233edc3`](https://github.com/Rizhiy/pycs/commit/233edc3d6b322894b0e614ab6441d72140544a74))

* feat: load file ([`51677c6`](https://github.com/Rizhiy/pycs/commit/51677c6940247bd40dd977a5f68f2904c2dfa002))

* feat: clone method ([`93782c4`](https://github.com/Rizhiy/pycs/commit/93782c454b3e138b900cfa7e860c4f8e6b576390))

* feat: required config leaf ([`a3ecea0`](https://github.com/Rizhiy/pycs/commit/a3ecea088df5d7decd685c9665a8bead5809b7ca))

* feat: add str magic ([`9b3c406`](https://github.com/Rizhiy/pycs/commit/9b3c406a23488891d38d1c754bd89113afe9a7bc))

### Fix

* fix(test_bad.py): Fix bad leaf name ([`280db94`](https://github.com/Rizhiy/pycs/commit/280db941b8f1b9fdf62ec0b634fda79c5a5e1c2b))

* fix(node.py): Fix CN(new_allowed=True) ([`9fe1c70`](https://github.com/Rizhiy/pycs/commit/9fe1c702dd114d3a048cd644bf42cbe24dd35f26))

* fix: format ([`bedf2f1`](https://github.com/Rizhiy/pycs/commit/bedf2f1c2022a14392ded4e7328c1cd9dc9e6d49))

### Refactor

* refactor: decompose set_new method ([`99fffa5`](https://github.com/Rizhiy/pycs/commit/99fffa5870fae5c87593cbc7b9dd4794108439d2))

### Style

* style(leaf.py): Adjust error message ([`0eade03`](https://github.com/Rizhiy/pycs/commit/0eade03153fc0b8e765d97a8a221dd3e32931443))

### Test

* test: add missing files ([`5186920`](https://github.com/Rizhiy/pycs/commit/5186920ab672e1cdfa16999deaa2c2b2130fa325))

* test(description): change configs structure ([`acd60c3`](https://github.com/Rizhiy/pycs/commit/acd60c3a4f7cdd327582dd157be36f6dbb2c9476))

* test(good): multiple inheritance loads ([`13298ef`](https://github.com/Rizhiy/pycs/commit/13298efb56445c4a8ee4f9874a7688cca7272c01))

### Unknown

* Merge branch &#39;feat/specific-class-in-errors&#39; into &#39;master&#39;

feat: write specific type in error

See merge request utilities/ntc!20 ([`0bb18dc`](https://github.com/Rizhiy/pycs/commit/0bb18dc7837941164ff56ff16ae3edde5ec79af3))

* Merge branch &#39;feat/improve-errors-text&#39; into &#39;master&#39;

feat: make meaningful errors for subclass

See merge request utilities/ntc!19 ([`0a9d9cf`](https://github.com/Rizhiy/pycs/commit/0a9d9cf9bb90f0cee4c0037e4ecebc4b4018524e))

* Merge branch &#39;feat/leaf-description&#39; into &#39;master&#39;

feat: add description field

See merge request utilities/ntc!18 ([`b843a63`](https://github.com/Rizhiy/pycs/commit/b843a63aea5f4fe491a8019384f3182ac771ad33))

* Merge branch &#39;test/multiple-loadings&#39; into &#39;master&#39;

test(good): multiple inheritance loads

See merge request utilities/ntc!17 ([`2db7166`](https://github.com/Rizhiy/pycs/commit/2db7166d5555aeb9242fd63963d9d22849df8011))

* Revert &#34;feat(ci): automate semantic release&#34;

This reverts commit d1e35a6beeab758a69c66a136a68c9448973e864. ([`4861a8f`](https://github.com/Rizhiy/pycs/commit/4861a8fba3c7cb6d942d56901353dcb713849376))

* fix[node.py]: Fix partial in node leaf_spec ([`9f74abd`](https://github.com/Rizhiy/pycs/commit/9f74abd6fd6121d00d07bdd1a3f23275bf4fc733))

* feat[leaf.py]: Added checks to work with functools.partial ([`4b950ed`](https://github.com/Rizhiy/pycs/commit/4b950edc8c4319f453e1c03c575309287f1c1c51))

* 0.11.0

Feature
* Automate semantic release (d1e35a6) ([`291d8fa`](https://github.com/Rizhiy/pycs/commit/291d8faee5eb3bf8a5ce1a8b5da4ae2045bed4e4))

* Merge branch &#39;feat/semantic-release&#39; into &#39;master&#39;

feat(ci): automate semantic release

See merge request utilities/ntc!16 ([`1d81a8c`](https://github.com/Rizhiy/pycs/commit/1d81a8c5ab67def0d606c795568d9ae42a57a4f2))

* 0.10.0 ([`481fe6a`](https://github.com/Rizhiy/pycs/commit/481fe6ad7619459164fc3543e666ce6d7723c535))

* refactor[node.py]: Change clone() to inherit(), clone() now just clones ([`6bd74ed`](https://github.com/Rizhiy/pycs/commit/6bd74ed2bcdcb3616540c2007f8462681710b308))

* chore[__init__.py]: Version bump ([`889fd30`](https://github.com/Rizhiy/pycs/commit/889fd30b362a9ced28fd6530f9557533bd6df6a7))

* Merge branch &#39;master&#39; of 192.168.135.11:utilities/ntc ([`e9e58aa`](https://github.com/Rizhiy/pycs/commit/e9e58aa12d71c435a6aec25c68614379071b350a))

* Merge branch &#39;feat/assert-to-val-error&#39; into &#39;master&#39;

feat[node]: validation error instead of assertion

See merge request utilities/ntc!15 ([`d3ecbcc`](https://github.com/Rizhiy/pycs/commit/d3ecbcc426836a358fc691f517871adab78bf704))

* feat[node]: validation error instead of assertion ([`4237d62`](https://github.com/Rizhiy/pycs/commit/4237d62c46badad9957aee8def5a80005b19178b))

* Merge branch &#39;feat/ntu-setup-utils&#39; into &#39;master&#39;

feat[setup]: use ntu setup utils

See merge request utilities/ntc!14 ([`1e9c606`](https://github.com/Rizhiy/pycs/commit/1e9c606232d7c46bb77d23e37e5992ec53986533))

* feat[setup]: use ntu setup utils ([`37e38e6`](https://github.com/Rizhiy/pycs/commit/37e38e6cf8d05856cde0e6c629f71de370f622f5))

* Merge branch &#39;feat/helpful-errors&#39; into &#39;master&#39;

feat: helpful errors

See merge request utilities/ntc!13 ([`30a1e7c`](https://github.com/Rizhiy/pycs/commit/30a1e7c5007b9edb36c0a25183fe33dca7cc4c66))

* Merge branch &#39;master&#39; into &#39;feat/helpful-errors&#39;

# Conflicts:
#   ntc/__init__.py
#   ntc/leaf.py ([`8910b13`](https://github.com/Rizhiy/pycs/commit/8910b13b9e4c23bb147ca5f94322e21d8a5b2510))

* chore[node.py]: Change full_key to start with &#39;cfg&#39; ([`9eabdf7`](https://github.com/Rizhiy/pycs/commit/9eabdf7f33fe570d8f68875bf2bdd14272c0a935))

* feat[leaf.py]: Add more flexible specification and fix clone ([`b7c17d5`](https://github.com/Rizhiy/pycs/commit/b7c17d5698a680bdd78e096f58b4ebf9f968f446))

* func return type ([`591eaf9`](https://github.com/Rizhiy/pycs/commit/591eaf9526f95f1c9d8c7b74f6b1aa548a831da0))

* child_full_key; f-string; version ([`f6fb8bc`](https://github.com/Rizhiy/pycs/commit/f6fb8bcf4b8f52bb23211218f46c5f67d4d23fe3))

* change error text ([`8cb9ccd`](https://github.com/Rizhiy/pycs/commit/8cb9ccd0a5f3d011bba982f24bdcbce387bafd22))

* store full_key ([`6b5d134`](https://github.com/Rizhiy/pycs/commit/6b5d1348cb61ab5822bf071fdde7b165f9ab0ccd))

* Merge branch &#39;feat/dont-convert-types&#39; into &#39;master&#39;

feat: remove type set on assignment

See merge request utilities/config!12 ([`978ddd0`](https://github.com/Rizhiy/pycs/commit/978ddd01f56eb2b3a005273f1c5fe629ae22f34d))

* Merge branch &#39;feat/ntu-format-command&#39; into &#39;master&#39;

feat: ntu format command

See merge request utilities/config!11 ([`bd4c66d`](https://github.com/Rizhiy/pycs/commit/bd4c66d748bbac6f9805ee4cb7130160eb943cbf))

* refactor[node.py]: Make plain value to be set as required ([`fdfd9b2`](https://github.com/Rizhiy/pycs/commit/fdfd9b298eb4f3176da6d4b7540376514624449c))

* Merge branch &#39;feat/use-ntu&#39; into &#39;master&#39;

feat[ci]: use ntu

See merge request utilities/config!9 ([`0e6e1fc`](https://github.com/Rizhiy/pycs/commit/0e6e1fc171545317f9abce124af49b7a47ead93c))

* feat[ci]: use ntu ([`1b012dc`](https://github.com/Rizhiy/pycs/commit/1b012dc10a7b0bd7dbebd05ad96fdf2b7902dfd1))

* fix[config.py]: Fix handling of required subclass leaf_spec and add tests ([`150def7`](https://github.com/Rizhiy/pycs/commit/150def7ce42f3a23cf2985591becb71de93f1154))

* feat[config.py]: Make SchemaErrors messages more descriptive ([`0b3eb7f`](https://github.com/Rizhiy/pycs/commit/0b3eb7f93f239321de5679153cc09d0c1c6fce52))

* chore[tests]: Rename test_config.py to test_node.py ([`520ec85`](https://github.com/Rizhiy/pycs/commit/520ec853ffadebd9a92769ccf3dabffdd7947868))

* fix[config.py]: Fix leaf creation for required spec ([`e0e8eb7`](https://github.com/Rizhiy/pycs/commit/e0e8eb741055572a236d4e2a1f55d1d807b13ee0))

* refactor[config.py]: Change how config is loaded and import rules ([`4075acf`](https://github.com/Rizhiy/pycs/commit/4075acf7bd1f724cdd63441f16bd15bc829c4756))

* Merge branch &#39;feat/organise-tests&#39; into &#39;master&#39;

feat: organise tests

See merge request utilities/config!8 ([`80b6c88`](https://github.com/Rizhiy/pycs/commit/80b6c8848c3f2e53f3e612132c24f500b41ee3b5))

* docs[README.md]: Improve instructions ([`913e50a`](https://github.com/Rizhiy/pycs/commit/913e50a936983c050c8cecb7ad5bb2ce2a05b1ba))

* feat[config.py]: Add hooks ([`992e9be`](https://github.com/Rizhiy/pycs/commit/992e9be117ae9a0a9253da0bc908c168c807f0b5))

* Merge branch &#39;feat/readme&#39; into &#39;master&#39;

feat: add docs

See merge request utilities/config!7 ([`58f1226`](https://github.com/Rizhiy/pycs/commit/58f12262c213c565a12a17f9424426c1c6b48117))

* feat[config.py]: Allow passing leaf type directly to CfgNode ([`51f9bfe`](https://github.com/Rizhiy/pycs/commit/51f9bfe1ecbffa18987d1bc01cf0a06202054c0d))

* chore[config.py]: Remove impossible case ([`c261bda`](https://github.com/Rizhiy/pycs/commit/c261bdaeb5156d7f1c444217690e620e9e5623e9))

* chore[tests]: Make bad tests more uniform ([`010ec74`](https://github.com/Rizhiy/pycs/commit/010ec74eaaa48f3c111a901e7b21b1cdea02eb45))

* refactor[config.py]: Change how transoforms and validators are added ([`01ffe64`](https://github.com/Rizhiy/pycs/commit/01ffe6409431a6b31f8bb9d49a2e87f339266c8e))

* chore[__init__.py]: Version bump ([`d4f4d1c`](https://github.com/Rizhiy/pycs/commit/d4f4d1c8bf16937db4510338ebc434617819e7a6))

* chore[config.py]: Rename transformers to transforms ([`d2f91c4`](https://github.com/Rizhiy/pycs/commit/d2f91c46392295e3c31ac6b098e63e51c46328d4))

* feat[config.py]: Adjust transform and validate ([`88c6108`](https://github.com/Rizhiy/pycs/commit/88c61080ac1137e0e8e8af7487cd529fd6d92ac8))

* chore[.gitingore]: Add test config ([`4539b9d`](https://github.com/Rizhiy/pycs/commit/4539b9d65f8c667276f50dbee100ea89e2a1d5d8))

* Merge branch &#39;feat/validators-transformers&#39; into &#39;master&#39;

feat: validators, transformers

See merge request utilities/config!6 ([`d475495`](https://github.com/Rizhiy/pycs/commit/d4754950f56444ac8d3042df958f10af52ed2925))

* chore[test_files.py]: Add test for transform and validate ([`9fb912a`](https://github.com/Rizhiy/pycs/commit/9fb912adfd9a972f437a28701ec07d6cc7dc28fc))

* feat[config.py]: Add subclass option to CfgLeaf ([`aa1ce34`](https://github.com/Rizhiy/pycs/commit/aa1ce342890af5484736ff93a25701989c0d6714))

* feat[config.py]: Add initialisation from dict ([`e83cec3`](https://github.com/Rizhiy/pycs/commit/e83cec3f937d35f96e08401d43d77a05d5e9337d))

* feat[config.py]: Add dict functionality ([`8ee8ea9`](https://github.com/Rizhiy/pycs/commit/8ee8ea99e2cecd9621c93a9dc3310d43a153dfa9))

* change author&#39;s info ([`73bcb6e`](https://github.com/Rizhiy/pycs/commit/73bcb6e4910c485689ced1d66dcf249fd13ef128))

* Merge branch &#39;feat/load-file&#39; into &#39;master&#39;

feat: load file

See merge request utilities/config!5 ([`5ddda21`](https://github.com/Rizhiy/pycs/commit/5ddda2110489945c1fe764f37400e9af5ada3221))

* freeze in test_save_unfrozen ([`d1ef56e`](https://github.com/Rizhiy/pycs/commit/d1ef56e31282f0a15c0174edd1df6dbd5e2dacb9))

* new_allowed key ([`974b6d4`](https://github.com/Rizhiy/pycs/commit/974b6d4019afde31f7a301a76f22cb02935cf8ef))

* some renaming ([`f2305b2`](https://github.com/Rizhiy/pycs/commit/f2305b23fd8d481d103c5c4aded60c76df3886ea))

* check was_unfrozen; separate errors module; import resolve ([`cb885d4`](https://github.com/Rizhiy/pycs/commit/cb885d4b07b475d1d72699899448a48bb7f61f35))

* some ([`e74a36e`](https://github.com/Rizhiy/pycs/commit/e74a36eb38b2dc452c122bbcaeb75b175ab7c8ea))

* base config and save ([`2c94298`](https://github.com/Rizhiy/pycs/commit/2c9429888333e123b9a02b79442f3d636c307441))

* fix ([`d21e149`](https://github.com/Rizhiy/pycs/commit/d21e14993ee9d35f733beac16b2e1e7153de95ed))

* fix ([`ded42e8`](https://github.com/Rizhiy/pycs/commit/ded42e889333ed83247366ed2309c59f41e1212e))

* chore[tests]: Update ([`d5c04bb`](https://github.com/Rizhiy/pycs/commit/d5c04bb12c4f82798f39496e40cb4416c98bb3d3))

* refactor[base_cfg.py]: Change to to function ([`52ff270`](https://github.com/Rizhiy/pycs/commit/52ff270fb6520350310147d298ffd716e98e1160))

* fix[test_files.py]: Fix test_node ([`7c38917`](https://github.com/Rizhiy/pycs/commit/7c389173b2af2ca8f1a2a496830ba198159445af))

* feat[tests]: Add test for node restriction ([`657efff`](https://github.com/Rizhiy/pycs/commit/657efff673445c2fb591b9029a44e7a857d1fa56))

* chore[tests]: Add test for bad attribute ([`0755130`](https://github.com/Rizhiy/pycs/commit/0755130306b43b4cdddeaa5fed40a00f01032331))

* Merge branch &#39;master&#39; of 192.168.135.11:utilities/config ([`6fdedce`](https://github.com/Rizhiy/pycs/commit/6fdedce275e02696b6b1e59dab8a46a2c3ac9775))

* feat[tests]: Add file tests ([`f7971d8`](https://github.com/Rizhiy/pycs/commit/f7971d8c0a535e257957ef8cd1def3284953ccdf))

* Merge branch &#39;feat/deep-clone&#39; into &#39;master&#39;

feat: clone method

See merge request utilities/config!4 ([`6c478b1`](https://github.com/Rizhiy/pycs/commit/6c478b1b29bbe23dbc6bae51af63ff2360e51595))

* Merge branch &#39;feat/required-field&#39; into &#39;master&#39;

feat: required config leaf

See merge request utilities/config!3 ([`0dd2d1b`](https://github.com/Rizhiy/pycs/commit/0dd2d1b2cc00e0be16603b1c6e0b4f0c90ffe00d))

* Merge branch &#39;feat/print-beauty&#39; into &#39;master&#39;

feat: add str magic

See merge request utilities/config!2 ([`aba0784`](https://github.com/Rizhiy/pycs/commit/aba0784f563806cbedbd5c463f33c55b07da893e))

* Merge branch &#39;feat/config-framework&#39; into &#39;master&#39;

feat config: rough first version

See merge request utilities/config!1 ([`901f8ae`](https://github.com/Rizhiy/pycs/commit/901f8ae2bec096171faa8a5c4bef9860ea1dc640))

* feat config: rough first version ([`a2933f6`](https://github.com/Rizhiy/pycs/commit/a2933f683724d2bfc8af16f8ec35e94db8c2f033))

* init ([`216e40a`](https://github.com/Rizhiy/pycs/commit/216e40af2fcaeda0284c288e493c755c9d681382))
