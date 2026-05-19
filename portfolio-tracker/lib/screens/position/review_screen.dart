import 'package:flutter/material.dart';
import '../../models/position.dart';
import '../../services/firestore_service.dart';

class ReviewScreen extends StatefulWidget {
  final Position position;
  const ReviewScreen({super.key, required this.position});

  @override
  State<ReviewScreen> createState() => _ReviewScreenState();
}

class _ReviewScreenState extends State<ReviewScreen> {
  late final TextEditingController _reviewController;
  final _service = FirestoreService();
  bool _isLoading = false;
  bool _isDirty = false;

  @override
  void initState() {
    super.initState();
    _reviewController =
        TextEditingController(text: widget.position.review ?? '');
    _reviewController.addListener(() => setState(() => _isDirty = true));
  }

  @override
  void dispose() {
    _reviewController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() => _isLoading = true);
    try {
      await _service.updateReview(
          widget.position.id, _reviewController.text.trim());
      if (mounted) {
        setState(() => _isDirty = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('복기 메모가 저장되었습니다.')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('오류: $e')));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = widget.position;
    final returnRate = p.returnRate;
    final pnl = p.realizedPnl;
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Text('${p.symbol} 복기'),
        actions: [
          if (_isDirty)
            TextButton(
              onPressed: _isLoading ? null : _save,
              child: const Text('저장'),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 포지션 요약 카드
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(p.symbol,
                            style: const TextStyle(
                                fontSize: 20, fontWeight: FontWeight.bold)),
                        if (returnRate != null)
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: returnRate >= 0
                                  ? Colors.blue.shade50
                                  : Colors.red.shade50,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              '${returnRate >= 0 ? '+' : ''}${returnRate.toStringAsFixed(2)}%',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: returnRate >= 0
                                    ? Colors.blue
                                    : Colors.red,
                              ),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _InfoRow('진입가', '₩${_fmt(p.entryPrice)}'),
                    if (p.exitPrice != null)
                      _InfoRow('정리가', '₩${_fmt(p.exitPrice!)}'),
                    _InfoRow('수량', '${p.quantity}'),
                    if (pnl != null)
                      _InfoRow(
                        '실현 손익',
                        '${pnl >= 0 ? '+' : ''}₩${_fmt(pnl)}',
                        valueColor: pnl >= 0 ? Colors.blue : Colors.red,
                      ),
                    if (p.targetPrice != null)
                      _InfoRow('목표가', '₩${_fmt(p.targetPrice!)}'),
                    if (p.stopLoss != null)
                      _InfoRow('손절가', '₩${_fmt(p.stopLoss!)}'),
                    const Divider(height: 20),
                    Text('매수 근거',
                        style: TextStyle(
                            fontSize: 12, color: colorScheme.outline)),
                    const SizedBox(height: 4),
                    Text(p.entryReason,
                        style: const TextStyle(fontSize: 14)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text('복기 메모',
                style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: colorScheme.primary)),
            const SizedBox(height: 8),
            TextFormField(
              controller: _reviewController,
              maxLines: 10,
              decoration: const InputDecoration(
                hintText: '이 포지션에서 무엇을 배웠나요?\n'
                    '판단이 맞았던 부분과 틀렸던 부분은?\n'
                    '다음에 같은 상황이 오면 어떻게 할 건가요?',
                border: OutlineInputBorder(),
                alignLabelWithHint: true,
              ),
            ),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: (_isLoading || !_isDirty) ? null : _save,
              style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14)),
              child: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('저장', style: TextStyle(fontSize: 16)),
            ),
          ],
        ),
      ),
    );
  }

  String _fmt(double v) => v.toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},');
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  final Color? valueColor;
  const _InfoRow(this.label, this.value, {this.valueColor});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label,
              style: TextStyle(
                  fontSize: 13,
                  color: Theme.of(context).colorScheme.outline)),
          Text(value,
              style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: valueColor)),
        ],
      ),
    );
  }
}
