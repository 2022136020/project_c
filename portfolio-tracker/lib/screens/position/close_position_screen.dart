import 'package:flutter/material.dart';
import '../../models/position.dart';
import '../../services/firestore_service.dart';

class ClosePositionScreen extends StatefulWidget {
  final Position position;
  const ClosePositionScreen({super.key, required this.position});

  @override
  State<ClosePositionScreen> createState() => _ClosePositionScreenState();
}

class _ClosePositionScreenState extends State<ClosePositionScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.position.symbol} 매매'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '매도'),
            Tab(text: '추가 매수'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _SellTab(position: widget.position),
          _BuyMoreTab(position: widget.position),
        ],
      ),
    );
  }
}

// ── 매도 탭 ────────────────────────────────────────────────────
class _SellTab extends StatefulWidget {
  final Position position;
  const _SellTab({required this.position});

  @override
  State<_SellTab> createState() => _SellTabState();
}

class _SellTabState extends State<_SellTab> {
  final _formKey = GlobalKey<FormState>();
  final _exitPriceController = TextEditingController();
  final _quantityController = TextEditingController();
  final _service = FirestoreService();
  DateTime _exitDate = DateTime.now();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _quantityController.text =
        widget.position.quantity % 1 == 0
            ? widget.position.quantity.toInt().toString()
            : widget.position.quantity.toString();
  }

  @override
  void dispose() {
    _exitPriceController.dispose();
    _quantityController.dispose();
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
    final soldQty =
        double.parse(_quantityController.text.replaceAll(',', ''));
    final totalQty = widget.position.quantity;
    final isFullSell = soldQty >= totalQty;
    final pnl = (exitPrice - widget.position.entryPrice) * soldQty;
    final returnRate =
        (exitPrice - widget.position.entryPrice) / widget.position.entryPrice * 100;

    try {
      if (isFullSell) {
        // 전량 매도 → 포지션 종료
        await _service.closePosition(
          widget.position.id,
          exitPrice,
          _exitDate,
          widget.position.accountId,
          soldQty,
          widget.position.symbol,
        );
      } else {
        // 분할 매도 → 수량 차감 + 새 정리 완료 레코드 생성 + 입금
        await _service.partialSell(
          position: widget.position,
          soldQty: soldQty,
          exitPrice: exitPrice,
          exitDate: _exitDate,
        );
      }

      if (mounted) {
        Navigator.pop(context);
        showDialog(
          context: context,
          builder: (dialogContext) => AlertDialog(
            title: Text(isFullSell ? '매도 완료' : '분할 매도 완료'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('종목: ${widget.position.symbol}'),
                Text('매도 수량: ${soldQty % 1 == 0 ? soldQty.toInt() : soldQty}주'),
                Text(
                    '수익률: ${returnRate >= 0 ? '+' : ''}${returnRate.toStringAsFixed(2)}%'),
                Text(
                    '실현 손익: ${pnl >= 0 ? '+' : ''}₩${_fmt(pnl)}'),
                if (!isFullSell)
                  Text(
                      '잔여 수량: ${(totalQty - soldQty) % 1 == 0 ? (totalQty - soldQty).toInt() : (totalQty - soldQty)}주'),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(dialogContext),
                child: const Text('확인'),
              ),
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
    final maxQty = widget.position.quantity;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 포지션 요약
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(widget.position.symbol,
                        style: const TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 16)),
                    const SizedBox(height: 8),
                    _Row('진입가', '₩${_fmt(widget.position.entryPrice)}'),
                    _Row('보유 수량',
                        '${maxQty % 1 == 0 ? maxQty.toInt() : maxQty}주'),
                    _Row('매수 근거', widget.position.entryReason),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            // 매도가
            TextFormField(
              controller: _exitPriceController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: '매도가',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.price_change_outlined),
              ),
              validator: (v) {
                if (v == null || v.isEmpty) return '매도가를 입력해 주세요.';
                if (double.tryParse(v.replaceAll(',', '')) == null) {
                  return '숫자만 입력해 주세요.';
                }
                return null;
              },
              onChanged: (_) => setState(() {}),
            ),
            const SizedBox(height: 16),
            // 매도 수량
            TextFormField(
              controller: _quantityController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: '매도 수량',
                helperText: '최대 ${maxQty % 1 == 0 ? maxQty.toInt() : maxQty}주',
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.format_list_numbered),
              ),
              validator: (v) {
                if (v == null || v.isEmpty) return '수량을 입력해 주세요.';
                final qty = double.tryParse(v.replaceAll(',', ''));
                if (qty == null || qty <= 0) return '올바른 수량을 입력해 주세요.';
                if (qty > maxQty) {
                  return '보유 수량(${maxQty % 1 == 0 ? maxQty.toInt() : maxQty}주)을 초과할 수 없습니다.';
                }
                return null;
              },
              onChanged: (_) => setState(() {}),
            ),
            const SizedBox(height: 8),
            // 실시간 수익률 미리보기
            Builder(builder: (_) {
              final ep = double.tryParse(
                  _exitPriceController.text.replaceAll(',', ''));
              final qty = double.tryParse(
                  _quantityController.text.replaceAll(',', ''));
              if (ep == null || qty == null || qty <= 0) {
                return const SizedBox.shrink();
              }
              final r = (ep - widget.position.entryPrice) /
                  widget.position.entryPrice * 100;
              final pnl = (ep - widget.position.entryPrice) * qty;
              return Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: r >= 0 ? Colors.blue.shade50 : Colors.red.shade50,
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
                        '${pnl >= 0 ? '+' : ''}₩${_fmt(pnl)}',
                        style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: r >= 0 ? Colors.blue : Colors.red),
                      ),
                    ]),
                    Column(children: [
                      const Text('매도 대금', style: TextStyle(fontSize: 12)),
                      Text(
                        '₩${_fmt(ep * qty)}',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ]),
                  ],
                ),
              );
            }),
            const SizedBox(height: 16),
            // 날짜
            InkWell(
              onTap: _pickDate,
              child: InputDecorator(
                decoration: const InputDecoration(
                  labelText: '매도일',
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
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('매도', style: TextStyle(fontSize: 16)),
            ),
          ],
        ),
      ),
    );
  }

  String _fmt(double v) => v.abs().toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},');
}

// ── 추가 매수 탭 ───────────────────────────────────────────────
class _BuyMoreTab extends StatefulWidget {
  final Position position;
  const _BuyMoreTab({required this.position});

  @override
  State<_BuyMoreTab> createState() => _BuyMoreTabState();
}

class _BuyMoreTabState extends State<_BuyMoreTab> {
  final _formKey = GlobalKey<FormState>();
  final _priceController = TextEditingController();
  final _quantityController = TextEditingController();
  final _service = FirestoreService();
  DateTime _buyDate = DateTime.now();
  bool _isLoading = false;

  @override
  void dispose() {
    _priceController.dispose();
    _quantityController.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _buyDate,
      firstDate: widget.position.entryDate,
      lastDate: DateTime.now(),
    );
    if (picked != null) setState(() => _buyDate = picked);
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);

    final addPrice =
        double.parse(_priceController.text.replaceAll(',', ''));
    final addQty =
        double.parse(_quantityController.text.replaceAll(',', ''));

    try {
      await _service.addMorePosition(
        positionId: widget.position.id,
        currentQty: widget.position.quantity,
        currentEntryPrice: widget.position.entryPrice,
        addQty: addQty,
        addPrice: addPrice,
        accountId: widget.position.accountId,
        buyDate: _buyDate,
        symbol: widget.position.symbol,
      );
      if (mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('추가 매수가 반영되었습니다.')),
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

    return SingleChildScrollView(
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
                    Text(p.symbol,
                        style: const TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 16)),
                    const SizedBox(height: 8),
                    _Row('현재 평균단가', '₩${_fmt(p.entryPrice)}'),
                    _Row('현재 보유 수량',
                        '${p.quantity % 1 == 0 ? p.quantity.toInt() : p.quantity}주'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            TextFormField(
              controller: _priceController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: '추가 매수가',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.price_change_outlined),
              ),
              validator: (v) {
                if (v == null || v.isEmpty) return '매수가를 입력해 주세요.';
                if (double.tryParse(v.replaceAll(',', '')) == null) {
                  return '숫자만 입력해 주세요.';
                }
                return null;
              },
              onChanged: (_) => setState(() {}),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _quantityController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: '추가 매수 수량',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.format_list_numbered),
              ),
              validator: (v) {
                if (v == null || v.isEmpty) return '수량을 입력해 주세요.';
                final qty = double.tryParse(v.replaceAll(',', ''));
                if (qty == null || qty <= 0) return '올바른 수량을 입력해 주세요.';
                return null;
              },
              onChanged: (_) => setState(() {}),
            ),
            // 평균단가 미리보기
            Builder(builder: (_) {
              final addPrice = double.tryParse(
                  _priceController.text.replaceAll(',', ''));
              final addQty = double.tryParse(
                  _quantityController.text.replaceAll(',', ''));
              if (addPrice == null || addQty == null || addQty <= 0) {
                return const SizedBox.shrink();
              }
              final newAvg = (p.entryPrice * p.quantity +
                      addPrice * addQty) /
                  (p.quantity + addQty);
              final newQty = p.quantity + addQty;
              return Container(
                margin: const EdgeInsets.only(top: 8),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.indigo.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    Column(children: [
                      const Text('새 평균단가', style: TextStyle(fontSize: 12)),
                      Text('₩${_fmt(newAvg)}',
                          style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.indigo)),
                    ]),
                    Column(children: [
                      const Text('총 수량', style: TextStyle(fontSize: 12)),
                      Text(
                          '${newQty % 1 == 0 ? newQty.toInt() : newQty}주',
                          style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.indigo)),
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
                  labelText: '매수일',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.calendar_today_outlined),
                ),
                child: Text(
                  '${_buyDate.year}.${_buyDate.month.toString().padLeft(2, '0')}.${_buyDate.day.toString().padLeft(2, '0')}',
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
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('추가 매수', style: TextStyle(fontSize: 16)),
            ),
          ],
        ),
      ),
    );
  }

  String _fmt(double v) => v.abs().toStringAsFixed(0).replaceAllMapped(
      RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},');
}

class _Row extends StatelessWidget {
  final String label;
  final String value;
  const _Row(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label,
              style: const TextStyle(fontSize: 13, color: Colors.grey)),
          Text(value,
              style: const TextStyle(
                  fontSize: 13, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
