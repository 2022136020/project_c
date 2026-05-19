import 'package:flutter/material.dart';
import '../../models/position.dart';
import '../../services/firestore_service.dart';

class ClosePositionScreen extends StatefulWidget {
  final Position position;
  const ClosePositionScreen({super.key, required this.position});

  @override
  State<ClosePositionScreen> createState() => _ClosePositionScreenState();
}

class _ClosePositionScreenState extends State<ClosePositionScreen> {
  final _formKey = GlobalKey<FormState>();
  final _exitPriceController = TextEditingController();
  final _service = FirestoreService();

  DateTime _exitDate = DateTime.now();
  bool _isLoading = false;

  @override
  void dispose() {
    _exitPriceController.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _exitDate,
      firstDate: widget.position.entryDate,
      lastDate: DateTime.now(),
    );
    if (picked != null) setState(() => _exitDate = picked);
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    final exitPrice =
        double.parse(_exitPriceController.text.replaceAll(',', ''));
    final returnRate =
        (exitPrice - widget.position.entryPrice) / widget.position.entryPrice * 100;
    final pnl = (exitPrice - widget.position.entryPrice) * widget.position.quantity;

    try {
      await _service.closePosition(widget.position.id, exitPrice, _exitDate);
      if (mounted) {
        Navigator.pop(context);
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('포지션 정리 완료'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('종목: ${widget.position.symbol}'),
                Text('수익률: ${returnRate >= 0 ? '+' : ''}${returnRate.toStringAsFixed(2)}%'),
                Text('실현 손익: ${pnl >= 0 ? '+' : ''}₩${pnl.toStringAsFixed(0)}'),
              ],
            ),
            actions: [
              TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('확인')),
            ],
          ),
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
    return Scaffold(
      appBar: AppBar(title: Text('${widget.position.symbol} 정리')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('진입가: ₩${widget.position.entryPrice}'),
                      Text('수량: ${widget.position.quantity}'),
                      Text('매수 근거: ${widget.position.entryReason}'),
                      if (widget.position.targetPrice != null)
                        Text('목표가: ₩${widget.position.targetPrice}'),
                      if (widget.position.stopLoss != null)
                        Text('손절가: ₩${widget.position.stopLoss}'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _exitPriceController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: '정리가',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.price_change_outlined),
                ),
                validator: (v) {
                  if (v == null || v.isEmpty) return '정리가를 입력해 주세요.';
                  if (double.tryParse(v.replaceAll(',', '')) == null) return '숫자만 입력';
                  return null;
                },
                onChanged: (v) => setState(() {}),
              ),
              const SizedBox(height: 8),
              // 실시간 수익률 미리보기
              if (_exitPriceController.text.isNotEmpty)
                Builder(builder: (_) {
                  final ep = double.tryParse(
                      _exitPriceController.text.replaceAll(',', ''));
                  if (ep == null) return const SizedBox.shrink();
                  final r = (ep - widget.position.entryPrice) /
                      widget.position.entryPrice * 100;
                  final pnl = (ep - widget.position.entryPrice) *
                      widget.position.quantity;
                  return Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: r >= 0
                          ? Colors.blue.shade50
                          : Colors.red.shade50,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        Column(children: [
                          const Text('수익률', style: TextStyle(fontSize: 12)),
                          Text(
                            '${r >= 0 ? '+' : ''}${r.toStringAsFixed(2)}%',
                            style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: r >= 0 ? Colors.blue : Colors.red),
                          ),
                        ]),
                        Column(children: [
                          const Text('실현 손익', style: TextStyle(fontSize: 12)),
                          Text(
                            '${pnl >= 0 ? '+' : ''}₩${pnl.toStringAsFixed(0)}',
                            style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: r >= 0 ? Colors.blue : Colors.red),
                          ),
                        ]),
                      ],
                    ),
                  );
                }),
              const SizedBox(height: 16),
              InkWell(
                onTap: _pickDate,
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: '정리일',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.calendar_today_outlined),
                  ),
                  child: Text(
                    '${_exitDate.year}.${_exitDate.month.toString().padLeft(2, '0')}.${_exitDate.day.toString().padLeft(2, '0')}',
                  ),
                ),
              ),
              const SizedBox(height: 32),
              FilledButton(
                onPressed: _isLoading ? null : _submit,
                style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14)),
                child: _isLoading
                    ? const SizedBox(
                        height: 20, width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text('정리 완료', style: TextStyle(fontSize: 16)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
