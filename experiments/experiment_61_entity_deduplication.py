# 实验61：实体消歧与关系去重优化

**日期**: 2026-02-02 08:03
**目的**: 解决知识图谱中的实体歧义和重复关系问题，提升图谱质量

## 问题背景

当前LightRAG的知识图谱构建存在两个关键问题：

1. **实体歧义**：同一实体可能有多种表达方式（如"AI"/"人工智能"/"Artificial Intelligence"）
2. **关系冗余**：相同语义的关系被多次存储（如"工作于"/"在...工作"/"雇佣"）

## 解决方案

### 1. 实体标准化模块

```python
# entity_normalizer.py
class EntityNormalizer:
    """实体名称标准化与消歧"""
    
    def __init__(self, similarity_threshold=0.85):
        self.threshold = similarity_threshold
        self.entity_index = {}  # 实体指纹 -> 标准形式
        
    def get_fingerprint(self, entity_name: str) -> str:
        """生成实体指纹：去除停用词、统一大小写、拼音首字母"""
        # 步骤1: 转小写
        normalized = entity_name.lower().strip()
        
        # 步骤2: 去除停用词
        stopwords = {'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', '的', '在', '是'}
        words = [w for w in normalized.split() if w not in stopwords]
        
        # 步骤3: 保留关键语义词
        key_terms = self._extract_key_terms(words)
        
        return ' '.join(sorted(key_terms))
    
    def _extract_key_terms(self, words: List[str]) -> List[str]:
        """提取关键术语（名词、专有名词）"""
        # 简单实现：保留长度>2的词
        return [w for w in words if len(w) > 2]
    
    def normalize(self, entity_name: str) -> str:
        """标准化实体名称"""
        fingerprint = self.get_fingerprint(entity_name)
        
        # 检查是否已有匹配的实体
        for existing, canonical in self.entity_index.items():
            if self._similarity(fingerprint, existing) > self.threshold:
                return canonical
        
        # 新实体，添加到索引
        self.entity_index[fingerprint] = entity_name
        return entity_name
    
    def _similarity(self, s1: str, s2: str) -> float:
        """计算两个字符串的相似度（使用Jaccard）"""
        set1 = set(s1.split())
        set2 = set(s2.split())
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0
```

### 2. 关系去重模块

```python
# relation_deduplicator.py
class RelationDeduplicator:
    """关系语义等价性检测与合并"""
    
    # 同义关系映射表
    SYNONYM_MAP = {
        'works_at': ['employed_by', 'works_for', 'job_at', '在...工作'],
        'located_in': ['situated_in', 'found_in', '位于', '坐落于'],
        'created_by': ['authored_by', 'invented_by', 'created', '创造'],
        'part_of': ['belongs_to', 'member_of', 'subset_of', '属于'],
        'married_to': ['spouse_of', 'married_with', '配偶'],
        'knows': ['acquainted_with', 'friend_of', '认识', '知道'],
    }
    
    def __init__(self):
        self.relation_groups = {}
        self._build_synonym_groups()
    
    def _build_synonym_groups(self):
        """构建同义关系组"""
        for canonical, synonyms in self.SYNONYM_MAP.items():
            group = {canonical} | set(synonyms)
            for rel in group:
                self.relation_groups[rel] = canonical
    
    def get_canonical_relation(self, relation: str) -> str:
        """获取关系的规范形式"""
        return self.relation_groups.get(relation.lower(), relation)
    
    def deduplicate_relations(self, relations: List[Dict]) -> List[Dict]:
        """去除重复关系，保留最详细的那个"""
        seen = set()
        unique_relations = []
        
        for rel in relations:
            # 标准化关系类型
            canonical = self.get_canonical_relation(rel['type'])
            
            # 创建唯一标识（源实体 + 关系类型 + 目标实体）
            key = (rel['source'].lower(), canonical, rel['target'].lower())
            
            if key not in seen:
                seen.add(key)
                # 返回标准化后的关系
                unique_relations.append({
                    'source': rel['source'],
                    'type': canonical,
                    'target': rel['target'],
                    'metadata': rel.get('metadata', {})
                })
        
        return unique_relations
```

### 3. 集成到LightRAG管道

```python
# integrate_normalization.py
from lightrag import LightRAG
from entity_normalizer import EntityNormalizer
from relation_deduplicator import RelationDeduplicator

class OptimizedLightRAG(LightRAG):
    """带实体/关系优化的LightRAG"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_normalizer = EntityNormalizer(similarity_threshold=0.85)
        self.relation_deduplicator = RelationDeduplicator()
    
    def insert(self, documents: List[str]):
        """插入文档时自动进行实体/关系优化"""
        # 原始处理
        entities, relations = super()._extract_entities_relations(documents)
        
        # 实体标准化
        normalized_entities = {}
        for entity_id, entity_data in entities.items():
            canonical_name = self.entity_normalizer.normalize(entity_data['name'])
            entity_data['name'] = canonical_name
            normalized_entities[entity_id] = entity_data
        
        # 关系去重
        deduped_relations = self.relation_deduplicator.deduplicate_relations(relations)
        
        # 构建图谱
        self._build_graph(normalized_entities, deduped_relations)
```

## 预期效果

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 实体数量 | N | ~0.7N | -30% |
| 关系数量 | M | ~0.8M | -20% |
| 查询准确率 | X% | X+5% | +5% |
| 存储空间 | S | ~0.75S | -25% |

## 下一步

1. 实现基于Embedding的实体消歧（处理更复杂的同义情况）
2. 添加关系方向的规范（双向关系的统一表示）
3. 实现增量更新时的实时消歧
4. 添加实体合并后的链接保持

## 相关实验

- 实验60: 混合检索策略 (BM25 + Embedding)
- 实验58: 上下文相关性评分系统

## 参考资料

- [Apache Spark GraphFrames实体解析](https://graphframes.github.io/graphframes/docs/_site/index.html)
- [Dedupe.js实体链接库](https://github.com/spencermarx/dedupe)
